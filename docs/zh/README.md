# wikiR

[English](../../README.md) | [开发者说明](developer.md)

wikiR 是一个本地优先的个人知识库模板，用于搭建由智能体维护的个人 wiki / 材料库。它面向 Obsidian、Hermes 类本地智能体和本地 LLM 工作流。

这个项目提供 vault 目录结构、智能体工作契约、提示词配置和可检查的检索 harness，让你的材料可以在不依赖云端知识库的前提下被整理、检索和复用。

## 为什么需要 wikiR

- 本地优先：原始材料和笔记默认留在你的 vault 中。
- 智能体维护：用户用自然语言提出需求，智能体在后台调用工具。
- 兼容 Obsidian：笔记是普通 Markdown，使用扁平 YAML properties 和 wikilink。
- 重视证据链：原始材料先变成可追溯源卡，再被复用。
- 检索可控：上下文生成和检索检查是工作流的一部分，而不是事后补丁。
- 易扩展：词面检索开箱可用，后续可以接入本地 embedding 或 reranker。

## 工作方式

```text
原始材料
  -> 源卡
  -> 长期笔记
  -> 检索上下文
  -> 有依据的草稿和输出
```

用户不应该需要手动运行维护命令。本地智能体读取 `AGENTS.md`，调用 `harness/tool_manifest.json` 中定义的 wikiR 工具，然后把整理后的笔记或输出写回 vault。

## 核心目录

- `00_Inbox/materials/`：原始材料入口。
- `01_Sources/`：由原始材料生成的源卡。
- `02_Notes/`：长期笔记和可复用知识。
- `03_Projects/`：活跃项目工作区。
- `04_Outputs/`：草稿、申报书、报告和其他交付物。
- `80_Attachments/`：Obsidian 附件。
- `90_System/`：提示词、模板、索引、评估用例、上下文和日志。
- `harness/`：面向智能体的工具层和本地实现。

## 典型用法

1. 基于这个模板创建一个私有 vault。
2. 用 Obsidian 打开私有 vault。
3. 把 Hermes 或其他本地智能体的工作目录设为这个 vault。
4. 把新材料放入 `00_Inbox/materials/`。
5. 让智能体整理材料、查找可复用证据或生成输出草稿。

示例请求：

- “我放了新材料，请整理。”
- “帮我找一下和这个项目相关的可复用材料。”
- “基于已有 vault 材料写一份申报书草稿。”
- “检查一下这个 vault 有没有断链或检索问题。”

## 文档

- [架构说明](architecture.md)
- [Agent 运行时集成](agent-runtime.md)
- [公开模板与私有 Vault 工作流](open-source-template-and-private-vault.md)
- [开发者说明](developer.md)

## 默认安全边界

默认 `.gitignore` 会忽略原始材料、附件、生成索引、生成上下文、日志、密钥和 Obsidian 本地工作区状态。这能避免公开模板误提交私人内容。

真实个人使用时，建议把当前仓库作为公开模板维护，把实际 vault 放在另一个私有仓库中。
