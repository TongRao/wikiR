# wikiR

> Local-first personal wiki and document reuse harness for Obsidian, Hermes, and local LLM workflows.

wikiR is an open-source template for maintaining a local-first personal knowledge vault. It separates raw materials, source cards, durable notes, projects, outputs, prompts, and retrieval evaluation so a local agent can curate and reuse knowledge without turning the whole system into an opaque LLM workflow.

wikiR 是一个本地优先的个人 wiki / 材料库开源模板，面向 Obsidian、Hermes、本地 Qwen 35B MoE 等本地智能体工作流。它把原始材料、源卡、长期笔记、项目、输出、提示词和检索评估拆开，让本地智能体能够可追溯地整理和复用材料。

## Documentation / 文档

- English: [docs/en/README.md](docs/en/README.md)
- 中文：[docs/zh/README.md](docs/zh/README.md)

## Repository Model / 仓库模式

Use this repository as the public template and harness project. Use another private repository as your real personal vault.

建议把当前仓库作为公开模板和工具仓库维护；真实个人资料库放在另一个私有仓库中。

- English workflow: [docs/en/open-source-template-and-private-vault.md](docs/en/open-source-template-and-private-vault.md)
- 中文流程：[docs/zh/open-source-template-and-private-vault.md](docs/zh/open-source-template-and-private-vault.md)

## Quick Start / 快速开始

For the public template:

```sh
git clone <PUBLIC_WIKIR_REPO_URL> wikiR
cd wikiR
python3 harness/wiki.py doctor
```

To create a private working vault:

```sh
cd /path/to/workspace
git clone <PUBLIC_WIKIR_REPO_URL> wikiR-private
cd wikiR-private
git remote rename origin upstream
git remote add origin <PRIVATE_WIKIR_VAULT_REPO_URL>
git push -u origin main
```

Open `wikiR-private` in Obsidian and use it as the Hermes working directory.

## Common Commands / 常用命令

```sh
python3 harness/wiki.py init
python3 harness/wiki.py ingest
python3 harness/wiki.py build-index
python3 harness/wiki.py search "your question or task"
python3 harness/wiki.py context "your question or task"
python3 harness/wiki.py doctor
python3 harness/wiki.py eval
```

## Core Layout / 核心目录

- `00_Inbox/materials/`: raw material inbox / 原始材料入口
- `01_Sources/`: source cards / 源卡
- `02_Notes/`: durable notes / 长期笔记
- `03_Projects/`: project workspaces / 项目工作区
- `04_Outputs/`: deliverables / 成稿输出
- `80_Attachments/`: Obsidian attachments / Obsidian 附件
- `90_System/`: prompts, templates, indexes, evals, logs / 提示词、模板、索引、评估、日志
- `harness/`: local scripts / 本地脚本

## Safety / 安全边界

The default `.gitignore` excludes raw materials, attachments, generated indexes, generated context, logs, secrets, and local Obsidian workspace state. This keeps the public template safe by default.

默认 `.gitignore` 会忽略原始材料、附件、生成索引、生成上下文、日志、密钥和 Obsidian 本地状态，避免公开模板误提交私人内容。
