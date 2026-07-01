# wikiR Architecture / wikiR 架构

Full bilingual documentation:

- English: `docs/en/architecture.md`
- 中文：`docs/zh/architecture.md`

完整双语文档见：

- English: `docs/en/architecture.md`
- 中文：`docs/zh/architecture.md`

## Minimal Pipeline / 最小流水线

```mermaid
flowchart LR
  A["00_Inbox/materials<br/>raw files / 原始文件"] --> B["Hermes or local agent<br/>reads and curates / 读取并整理"]
  B --> C["01_Sources<br/>source cards / 源卡"]
  C --> D["02_Notes<br/>durable notes / 长期笔记"]
  C --> E["03_Projects<br/>project workspaces / 项目工作区"]
  D --> F["agent search and synthesis<br/>智能体搜索和综合"]
  E --> F
  F --> G["04_Outputs<br/>grounded outputs / 有依据的输出"]
  B --> H["90_System<br/>prompts and templates / 提示词和模板"]
```

## Design Choice / 设计选择

wikiR is a vault structure and agent operating contract, not a Python harness.

wikiR 是 vault 结构和智能体操作契约，不是 Python harness。

Document parsing, OCR, search, and model inference belong to Hermes or the chosen local runtime.

文档解析、OCR、搜索和模型推理属于 Hermes 或选定的本地运行时职责。
