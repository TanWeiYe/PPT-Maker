from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from flask import Flask, jsonify, render_template, request, send_file
from pptx import Presentation
from pptx.util import Inches, Pt

ROOT_DIR = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT_DIR / "web"
UPLOAD_DIR = WEB_DIR / "uploads"
GENERATED_DIR = WEB_DIR / "generated"
SKILL_DIR = ROOT_DIR / ".agents" / "skills" / "ppt-master"
SCRIPTS_DIR = SKILL_DIR / "scripts"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".pptx",
}


@dataclass
class SessionData:
    session_id: str
    root: Path
    upload_dir: Path
    generated_dir: Path


app = Flask(__name__)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def init_session(session_id: str | None = None) -> SessionData:
    sid = session_id or str(uuid.uuid4())
    root = WEB_DIR / "runtime" / sid
    upload_dir = root / "uploads"
    generated_dir = root / "generated"
    ensure_dir(upload_dir)
    ensure_dir(generated_dir)
    return SessionData(session_id=sid, root=root, upload_dir=upload_dir, generated_dir=generated_dir)


def run_script(args: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            args,
            cwd=str(ROOT_DIR),
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return False, str(exc)
    output = "\n".join([result.stdout.strip(), result.stderr.strip()]).strip()
    return result.returncode == 0, output


def normalize_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def simple_outline_from_prompt(prompt: str) -> str:
    prompt = prompt.strip()
    if not prompt:
        return "1. 封面\n2. 背景与问题\n3. 核心内容\n4. 总结"

    sentences = re.split(r"[。！？!?.]\s*", prompt)
    points = [s.strip() for s in sentences if s.strip()]
    if not points:
        points = [prompt]

    top = [f"{index}. {point[:36]}" for index, point in enumerate(points[:8], start=1)]
    if top[-1] != f"{len(top)+1}. 总结":
        top.append(f"{len(top)+1}. 总结")
    return "\n".join(top)


def parse_outline_to_slides(outline_text: str) -> list[tuple[str, list[str]]]:
    lines = normalize_lines(outline_text)
    slides: list[tuple[str, list[str]]] = []
    current_title = ""
    bullets: list[str] = []

    def flush() -> None:
        nonlocal current_title, bullets
        if current_title:
            slides.append((current_title, bullets[:]))
            current_title = ""
            bullets = []

    for line in lines:
        if re.match(r"^(#|\d+[.)]|[一二三四五六七八九十]+[、.])", line):
            flush()
            current_title = re.sub(r"^(#\s*|\d+[.)]\s*|[一二三四五六七八九十]+[、.]\s*)", "", line).strip() or "未命名页面"
        elif line.startswith(("-", "*", "•")):
            bullets.append(line.lstrip("-*• ").strip())
        else:
            if current_title:
                bullets.append(line)
            else:
                current_title = line

    flush()
    if not slides:
        slides = [("封面", ["学生向美观演示"]), ("内容", ["请补充详细大纲"])]
    return slides


def apply_template_if_provided(session: SessionData, template_file: Path | None) -> Path | None:
    if not template_file:
        return None
    target = session.root / "template.pptx"
    shutil.copy2(template_file, target)
    return target


def build_pptx(slides: Iterable[tuple[str, list[str]]], output_path: Path, template_path: Path | None = None) -> None:
    prs = Presentation(str(template_path)) if template_path else Presentation()

    for index, (title, bullets) in enumerate(slides):
        layout = prs.slide_layouts[0] if index == 0 else prs.slide_layouts[1]
        slide = prs.slides.add_slide(layout)

        if slide.shapes.title:
            slide.shapes.title.text = title

        if len(slide.placeholders) > 1:
            text_frame = slide.placeholders[1].text_frame
            text_frame.clear()
            if bullets:
                text_frame.text = bullets[0]
                text_frame.paragraphs[0].font.size = Pt(24)
                for bullet in bullets[1:]:
                    paragraph = text_frame.add_paragraph()
                    paragraph.text = bullet
                    paragraph.level = 0
                    paragraph.font.size = Pt(20)
            else:
                text_frame.text = ""
        else:
            textbox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(3.5))
            tf = textbox.text_frame
            for bullet in bullets or [""]:
                p = tf.add_paragraph()
                p.text = bullet
                p.font.size = Pt(20)

    prs.save(str(output_path))


def save_uploaded_files(session: SessionData, files) -> list[Path]:
    saved: list[Path] = []
    for incoming in files:
        if not incoming.filename:
            continue
        suffix = Path(incoming.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            continue
        safe_name = f"{uuid.uuid4().hex}{suffix}"
        target = session.upload_dir / safe_name
        incoming.save(target)
        saved.append(target)
    return saved


def convert_sources_with_ppt_master(uploaded: list[Path], session: SessionData, source_url: str | None) -> list[Path]:
    converted: list[Path] = []
    for file_path in uploaded:
        suffix = file_path.suffix.lower()
        converter = None
        if suffix == ".pdf":
            converter = SCRIPTS_DIR / "source_to_md" / "pdf_to_md.py"
        elif suffix in {".doc", ".docx"}:
            converter = SCRIPTS_DIR / "source_to_md" / "doc_to_md.py"

        if converter and converter.exists():
            ok, _ = run_script(["python3", str(converter), str(file_path)])
            candidate = file_path.with_suffix(".md")
            if ok and candidate.exists():
                converted.append(candidate)
                continue
        if suffix in {".md", ".txt"}:
            converted.append(file_path)

    if source_url:
        web_converter = SCRIPTS_DIR / "source_to_md" / "web_to_md.py"
        if web_converter.exists():
            ok, _ = run_script(["python3", str(web_converter), source_url])
            if ok:
                maybe = Path.cwd() / "web.md"
                if maybe.exists():
                    moved = session.upload_dir / f"web_{uuid.uuid4().hex}.md"
                    shutil.move(str(maybe), moved)
                    converted.append(moved)

    return converted


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/outline")
def generate_outline():
    session_id = request.form.get("session_id")
    prompt = request.form.get("prompt", "")
    source_url = request.form.get("source_url", "").strip() or None

    session = init_session(session_id)
    uploaded = save_uploaded_files(session, request.files.getlist("files"))
    converted = convert_sources_with_ppt_master(uploaded, session, source_url)

    merged_context = [prompt.strip()]
    for file_path in converted:
        try:
            merged_context.append(file_path.read_text(encoding="utf-8", errors="ignore")[:4000])
        except OSError:
            continue

    outline = simple_outline_from_prompt("\n".join([item for item in merged_context if item]))
    payload = {
        "session_id": session.session_id,
        "outline": outline,
        "uploaded_files": [path.name for path in uploaded],
    }
    (session.root / "outline.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return jsonify(payload)


@app.post("/api/generate")
def generate_pptx():
    data = request.get_json(silent=True) or {}
    session = init_session(data.get("session_id"))

    outline = data.get("outline", "")
    if not outline:
        return jsonify({"error": "outline is required"}), 400

    template_name = data.get("template_name", "")
    template_file = session.upload_dir / template_name if template_name else None
    template_path = apply_template_if_provided(session, template_file if template_file and template_file.exists() else None)

    slides = parse_outline_to_slides(outline)
    output_path = session.generated_dir / "presentation.pptx"
    build_pptx(slides, output_path, template_path)

    return jsonify(
        {
            "session_id": session.session_id,
            "file": output_path.name,
            "download_url": f"/api/download/{session.session_id}/{output_path.name}",
            "quality": {
                "visual": "统一主题和布局基础可用，可继续优化品牌样式",
                "content": "按大纲拆页生成，可继续补充细节",
                "generation": "输出为可编辑 PPTX，支持下载",
            },
        }
    )


@app.get("/api/download/<session_id>/<filename>")
def download(session_id: str, filename: str):
    file_path = WEB_DIR / "runtime" / session_id / "generated" / filename
    if not file_path.exists():
        return jsonify({"error": "file not found"}), 404
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    ensure_dir(WEB_DIR / "runtime")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
