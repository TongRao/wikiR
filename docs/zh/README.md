# wikiR 中文文档

wikiR 是一个本地优先的个人 wiki / 材料库开源模板，面向 Obsidian、Hermes、本地 Qwen 35B MoE 等本地智能体工作流。

它不是一个云端知识库，也不要求你把材料交给在线服务。它提供的是一套可复制的本地 vault 结构、agent 工作契约、提示词模板和可解释的检索 harness。

## 适用场景

- 用 Obsidian 管理个人长期知识库。
- 把 PDF、Word、Excel、Markdown 等材料整理成可追溯源卡。
- 让本地智能体基于已有材料写申报书、方案、报告或项目草稿。
- 用简单的 harness 管住索引、检索、上下文生成和评估，不完全依赖 LLM 黑箱。

## 推荐仓库模式

建议使用两个仓库：

- 公开仓库：维护 wikiR 模板、harness、提示词、模板、示例和文档。
- 私有仓库：存放真实个人 vault、源卡、笔记、项目输出和可选原始材料。

详细流程见：[公开模板与私有 Vault 工作流](open-source-template-and-private-vault.md)。

## 快速开始

如果你只是维护开源模板：

```sh
git clone <PUBLIC_WIKIR_REPO_URL> wikiR
cd wikiR
python3 harness/wiki.py doctor
```

如果你要创建真实使用的私有 vault：

```sh
cd /path/to/workspace
git clone <PUBLIC_WIKIR_REPO_URL> wikiR-private
cd wikiR-private
git remote rename origin upstream
git remote add origin <PRIVATE_WIKIR_VAULT_REPO_URL>
git push -u origin main
```

然后用 Obsidian 打开 `wikiR-private`，把 Hermes 的工作目录也设为这个私有 vault。

## 常用命令

```sh
# 初始化/补齐目录
python3 harness/wiki.py init

# 扫描 00_Inbox/materials，生成 01_Sources 源卡
python3 harness/wiki.py ingest

# 为 Sources / Notes / Projects / Outputs 建本地文本索引
python3 harness/wiki.py build-index

# 命令行检索
python3 harness/wiki.py search "你的问题或任务"

# 生成给本地模型使用的上下文文件
python3 harness/wiki.py context "你的问题或任务"

# 检查 frontmatter、断链、索引新鲜度
python3 harness/wiki.py doctor

# 用 90_System/evals/retrieval_cases.jsonl 做检索回归测试
python3 harness/wiki.py eval
```

## 目录约定

- `00_Inbox/materials/`：新增原始材料入口。默认不自动移动、不删除。
- `01_Sources/`：每份原始材料对应的源卡，记录摘要、核心点、摘录、来源路径和处理状态。
- `02_Notes/`：长期可复用的原子化知识。
- `03_Projects/`：项目工作区，放需求、方案、计划、申报书素材组织。
- `04_Outputs/`：成稿、申报书、方案、报告等输出。
- `80_Attachments/`：Obsidian 附件。
- `90_System/`：系统提示词、模板、索引、评估用例、日志。
- `harness/`：本地脚本。

## Hermes / 本地模型接入

Hermes 或其他本地 agent runner 只需要遵守 `AGENTS.md`：

- 整理材料前调用 `ingest`。
- 写作前调用 `build-index` 和 `context`。
- 重要变更后调用 `doctor`。
- 检索质量变差时补充 `90_System/evals/retrieval_cases.jsonl`，再跑 `eval`。

当前 harness 是零第三方依赖的词面检索基线，适合作为可解释底座。后续可以加入本地 embedding 或 reranker，但不需要改变 vault 目录结构。

## Obsidian 写作标准

- 每个正式 Markdown 文件使用顶部 YAML properties。
- properties 保持扁平：`type`、`status`、`created`、`updated`、`tags`、`aliases`、`source_path` 等。
- 内部链接优先使用 Obsidian wikilink 格式。
- 不把长段正文塞进 properties；正文内容放到标题结构里。
- 文件名避免 `# | ^ : %% [[ ]]` 等容易破坏链接的字符。

## 更多文档

- [架构说明](architecture.md)
- [公开模板与私有 Vault 工作流](open-source-template-and-private-vault.md)
