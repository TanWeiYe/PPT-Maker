# UI-UX-PRO-MAX

A project setup for integrating and using the "UI-UX-PRO-MAX" skill within development workflows.

## Overview

UI-UX-PRO-MAX is a specialized skill package focused on advanced UI/UX design analysis and implementation guidance. It provides structured prompts and workflows to:

- Analyze and improve user interfaces
- Build modern, responsive component systems
- Elevate visual hierarchy and interaction patterns
- Apply practical UX principles to real codebases

## Installation

Clone or copy this repository's contents into your project under:

```
.agents/skills/ui-ux-pro-max/
```

So the final structure should look like:

```
.agents/skills/ui-ux-pro-max/
  skill.yaml
  README.md
  prompts/
    skill.md
```

## Usage

In your Copilot Chat (Agent mode), invoke the skill by asking for UI/UX enhancement tasks and referencing this skill context.

Example prompts:

- "Use UI-UX-PRO-MAX to redesign this dashboard for clarity and responsiveness."
- "Apply UI-UX-PRO-MAX heuristics to this form and suggest code-level improvements."
- "Refactor this component tree with a scalable design-system approach using UI-UX-PRO-MAX."

## Notes

- `skill.yaml` provides repository-standard metadata and trigger/usage entry points.
- `prompts/skill.md` contains the detailed upstream prompt instructions.
- You can customize prompt content to match your team style guide, design tokens, and accessibility requirements.
- For best results, pair with your project's coding standards and existing component library.
