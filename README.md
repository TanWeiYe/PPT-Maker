# PPT-Maker

网页端 MVP（先网页、后扩展）：

- 接收用户输入（对话文本、网页链接、文件上传）
- 生成可编辑文本大纲
- 基于大纲生成可编辑 PPTX 并下载
- 保留与 `.agents/skills/ppt-master` 深度集成的扩展点

## 快速开始

```bash
cd /path/to/PPT-Maker
python3 -m pip install -r requirements.txt
python3 web/app.py
```

浏览器访问：`http://127.0.0.1:5000`

## 当前能力与范围

### 已实现（MVP）

1. 面向学生场景的网页入口与交互
2. 流程 A：对话/素材输入 → 文本大纲生成 → PPTX 生成
3. 输入支持：PDF、Word、文本、图片、网页链接（转换能力按安装依赖生效）
4. 输出：`.pptx`，每页标题与正文元素可在 PowerPoint 中继续编辑

### 前后端联调能力

- 前端页面：`web/templates/index.html`
- 后端 API：
  - `POST /api/outline`：输入文本/文件/链接，生成可编辑大纲
  - `POST /api/generate`：输入大纲，生成可下载的 PPTX
  - `GET /api/download/<session_id>/<filename>`：下载生成结果
  - `GET /api/sample`：获取示例数据，快速验证流程

### 示例数据

- 示例配置文件：`examples/sample-data.json`
- 前端点击“加载示例数据”即可自动填充 prompt、链接和大纲，再一键走通生成流程。

### 模板能力

- 支持上传模板文件（`.pptx`）作为后续增强入口
- 当前生成器优先保证主流程闭环，模板深度改写将由后续接入 `ppt-master` 扩展

### 暂不实现

- 问题 7/8 对应能力先保留扩展接口，后续迭代

## 与 ppt-master 的关系

- 网页端负责接收文件、AI 对话入口、结果下载
- 复杂内容生产与高保真生成能力可继续下沉到 `ppt-master` 脚本流水线
- 本仓库已保留技能目录：`.agents/skills/ppt-master`

## 本地运行方式

```bash
cd "$(git rev-parse --show-toplevel)"
python3 -m pip install -r requirements.txt
python3 web/app.py
```

浏览器访问：`http://127.0.0.1:5000`

## 测试验证

执行后端自动化测试：

```bash
cd "$(git rev-parse --show-toplevel)"
python3 -m unittest discover -s tests -v
```

测试覆盖内容：

1. 示例数据接口可访问
2. 大纲生成接口可用
3. PPT 生成与下载链路可用（含产物合法性检查）
