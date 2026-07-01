# wikiR 开发者说明

[English](../en/developer.md) | [README](README.md)

这份文档面向维护者，以及需要把 wikiR 接入 Hermes 等本地 agent runtime 的人。公开 README 会尽量面向普通用户；实现细节、私有 vault 搭建和调试说明放在这里。

## 仓库策略

建议使用两个仓库：

- 公开模板仓库：维护架构、harness、提示词、模板、示例和文档。
- 私有 vault 仓库：存放真实源卡、笔记、项目输出，以及可选的原始材料。

公开仓库不应该包含私人材料、生成索引、生成上下文、日志、密钥或 Obsidian 本地工作区状态。

## 创建私有 Vault

公开模板推送完成后，创建私有工作 vault：

```sh
cd /path/to/workspace
git clone <PUBLIC_WIKIR_REPO_URL> my-wikiR
cd my-wikiR
git remote rename origin upstream
git remote add origin <PRIVATE_WIKIR_VAULT_REPO_URL>
git push -u origin main
```

然后用 Obsidian 打开 `my-wikiR`，并把它作为 Hermes 工作目录。

## 把模板更新同步到私有 Vault

```sh
cd /path/to/my-wikiR
git fetch upstream
git merge upstream/main
```

合并后，让 Hermes 或本地 agent 调用 `wiki_doctor`。

## Agent 工具层

工具定义在：

```text
harness/tool_manifest.json
```

JSON 适配器是：

```text
harness/wiki_tool.py
```

Hermes 或其他 runtime 应该绑定这些工具，并在后台自动调用。用户通常只需要自然语言提出需求，不应该日常进入 terminal 运行命令。

工具名：

- `wiki_init`
- `wiki_ingest`
- `wiki_build_index`
- `wiki_search`
- `wiki_context`
- `wiki_doctor`
- `wiki_eval`

## Hermes 项目提示词

配置 Hermes 时，可以使用下面这段项目级说明：

```text
你正在维护一个 wikiR vault。用户不应该手动运行 harness 命令；你需要在后台调用 wikiR 工具。

工作目录是当前 vault 根目录。先阅读 AGENTS.md、harness/tool_manifest.json 和 90_System/prompts/。

处理新材料时，调用 wiki_ingest，再整理 01_Sources 中的源卡，必要时沉淀到 02_Notes。

回答资料查找类问题时，先调用 wiki_build_index，再调用 wiki_search。

写申报书、方案、报告、总结等复用型任务时，先调用 wiki_build_index，再调用 wiki_context，读取 90_System/context/last_context.md 后再写作。

重要修改后调用 wiki_doctor；修改检索逻辑或 eval cases 后调用 wiki_eval。

不要上传文件，不要删除原始材料，不要把检索不到的内容编造成事实。
```

## 调试工具层

CLI 是确定性实现和调试兜底，不是日常用户入口。

验证 JSON 工具适配器：

```sh
python3 harness/wiki_tool.py '{"tool":"wiki_doctor","args":{}}'
python3 harness/wiki_tool.py '{"tool":"wiki_search","args":{"query":"本地知识库 申报书","top_k":5}}'
python3 harness/wiki_tool.py '{"tool":"wiki_eval","args":{}}'
```

必要时验证底层 CLI：

```sh
python3 harness/wiki.py doctor
python3 harness/wiki.py eval
```

## 公开推送安全检查

提交到公开仓库前运行：

```sh
git status --short --ignored
git check-ignore -v 00_Inbox/materials/*
git check-ignore -v 90_System/context/last_context.md
git check-ignore -v 90_System/index/wiki_index.jsonl
git add -n .
```

暂存区里应该只有模板文件、提示词、harness 代码、文档和安全示例。

## 私有原始材料管理方式

在私有 vault 中选择一种方式：

- 保留默认 ignore，只跟踪整理后的 Markdown。
- 用 `git add -f` 选择性加入私人文件。
- 在存储和隐私条件允许时，用 Git LFS 跟踪原始材料。

不要因为某个私有 vault 需要不同的材料跟踪策略，就修改公开模板的默认安全规则。
