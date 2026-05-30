let sessionId = "";
let templateName = "";

const outlineBtn = document.getElementById("outlineBtn");
const generateBtn = document.getElementById("generateBtn");
const logBox = document.getElementById("log");
const downloadLink = document.getElementById("downloadLink");

function log(message) {
  logBox.textContent += `${message}\n`;
}

outlineBtn.addEventListener("click", async () => {
  const prompt = document.getElementById("prompt").value;
  const sourceUrl = document.getElementById("sourceUrl").value;
  const files = document.getElementById("files").files;

  const body = new FormData();
  body.append("session_id", sessionId);
  body.append("prompt", prompt);
  body.append("source_url", sourceUrl);
  for (const file of files) {
    body.append("files", file);
  }

  log("正在生成大纲...");
  const response = await fetch("/api/outline", { method: "POST", body });
  const data = await response.json();

  if (!response.ok) {
    log(`大纲生成失败: ${data.error || response.statusText}`);
    return;
  }

  sessionId = data.session_id;
  templateName = data.template_name || "";
  document.getElementById("outline").value = data.outline || "";
  log(`大纲生成完成，session: ${sessionId}`);
});

generateBtn.addEventListener("click", async () => {
  const outline = document.getElementById("outline").value;
  if (!outline.trim()) {
    log("请先生成或填写大纲");
    return;
  }

  log("正在生成 PPTX...");
  const response = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, outline, template_name: templateName }),
  });

  const data = await response.json();
  if (!response.ok) {
    log(`PPTX 生成失败: ${data.error || response.statusText}`);
    return;
  }

  sessionId = data.session_id;
  downloadLink.href = data.download_url;
  downloadLink.classList.remove("hidden");
  downloadLink.textContent = "下载可编辑 PPTX";
  log("PPTX 已生成，可下载。\n质量信息: " + JSON.stringify(data.quality));
});
