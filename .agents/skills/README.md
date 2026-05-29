# Skills Directory

项目级技能目录：`.agents/skills/`

## 目录规范

- 每个技能必须放在独立目录：`.agents/skills/<skill-name>/`
- `<skill-name>` 必须匹配正则：`^[a-z0-9]([a-z0-9-]*[a-z0-9])?$`
- 每个技能目录至少包含：
  - `skill.yaml`
  - `README.md`

## 建议文件

- `install.sh`：安装脚本（可选）
- `examples/`：示例输入输出（可选）

## 最小 skill.yaml 约定

至少包含以下顶层字段：

- `name`
- `description`
- `triggers`
- `usage`

以上字段由 CI 工作流 `.github/workflows/validate-agent-skills.yml` 强制校验。
