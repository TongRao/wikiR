---
type: note
status: active
created: 2026-07-01
updated: 2026-07-01
tags:
  - wikiR
  - system-design
  - local-first
aliases:
  - wikiR 系统设计原则
---
# wikiR 系统设计原则

## 核心原则

- 本地优先：默认不依赖云端服务，不上传原始材料。
- 原始材料可追溯：所有整理后的源卡都要保留 `source_path`、`material_id` 和摘录。
- 人工可维护：目录、frontmatter、模板和评估用例都必须能被人直接读懂和修改。
- 检索可评估：重要写作任务先搜索并读取相关材料，再基于证据写作。
- 模型可替换：Hermes、本地 Qwen 或其他 runner 只需要遵守统一目录、提示词和模板，不绑定某一个模型服务。

## 工作边界

- `01_Sources/` 保存材料级理解。
- `02_Notes/` 保存跨项目复用的稳定知识。
- `03_Projects/` 保存项目语境和任务推进。
- `04_Outputs/` 保存面向交付的成稿。

## 后续扩展

- 接入本地 OCR，增强扫描 PDF 和图片材料读取能力。
- 接入本地语义搜索或 reranker，但作为 runtime 能力，不进入 vault 格式本身。
- 增加人工维护的检查清单，覆盖项目申报、技术方案、个人经历、产品资料等高频任务。
