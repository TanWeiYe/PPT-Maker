let currentSessionId = "";
let currentTemplateName = "";

const outlineBtn = document.getElementById("outlineBtn");
const sampleBtn = document.getElementById("sampleBtn");
const generateBtn = document.getElementById("generateBtn");
const logBox = document.getElementById("log");
const downloadLink = document.getElementById("downloadLink");

function log(message) {
  logBox.textContent += `${message}\n`;
}

sampleBtn.addEventListener("click", async () => {
  log("正在加载示例数据...");
  try {
    const response = await fetch("/api/sample");
    const data = await response.json();
    if (!response.ok) {
      log(`示例数据加载失败: ${data.error || response.statusText}`);
      return;
    }
    document.getElementById("prompt").value = data.prompt || "";
    document.getElementById("sourceUrl").value = data.source_url || "";
    document.getElementById("outline").value = data.outline || "";
    log(`示例数据已加载: ${data.title || "示例"}`);
  } catch (error) {
    log(`示例数据加载失败: ${error.message}`);
  }
});

outlineBtn.addEventListener("click", async () => {
  const prompt = document.getElementById("prompt").value;
  const sourceUrl = document.getElementById("sourceUrl").value;
  const files = document.getElementById("files").files;

  const body = new FormData();
  body.append("session_id", currentSessionId);
  body.append("prompt", prompt);
  body.append("source_url", sourceUrl);
  for (const file of files) {
    body.append("files", file);
  }

  log("正在生成大纲...");
  try {
    const response = await fetch("/api/outline", { method: "POST", body });
    const data = await response.json();

    if (!response.ok) {
      log(`大纲生成失败: ${data.error || response.statusText}`);
      return;
    }

    currentSessionId = data.session_id;
    currentTemplateName = data.template_name || "";
    document.getElementById("outline").value = data.outline || "";
    log(`大纲生成完成，session: ${currentSessionId}`);
  } catch (error) {
    log(`大纲生成失败: ${error.message}`);
  }
});

generateBtn.addEventListener("click", async () => {
  const outline = document.getElementById("outline").value;
  if (!outline.trim()) {
    log("请先生成或填写大纲");
    return;
  }

  log("正在生成 PPTX...");
  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: currentSessionId, outline, template_name: currentTemplateName }),
    });

    const data = await response.json();
    if (!response.ok) {
      log(`PPTX 生成失败: ${data.error || response.statusText}`);
      return;
    }

    currentSessionId = data.session_id;
    downloadLink.href = data.download_url;
    downloadLink.classList.remove("hidden");
    downloadLink.textContent = "下载可编辑 PPTX";
    log("PPTX 已生成，可下载。\n质量信息: " + JSON.stringify(data.quality));
  } catch (error) {
    log(`PPTX 生成失败: ${error.message}`);
  }
});
