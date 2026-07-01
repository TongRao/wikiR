# Agent 运行时集成

wikiR 的正常使用方式不是让用户打开终端运行一堆 Python 命令，而是：

1. 用户在 Obsidian 或 Hermes 中用自然语言提出需求。
2. Hermes 根据 `AGENTS.md` 判断需要哪些 wikiR 工具。
3. Hermes 调用 `harness/tool_manifest.json` 中定义的工具。
4. 工具层在后台维护源卡、索引、上下文和评估结果。
5. 用户只看到整理后的笔记、检索依据、草稿或检查结果。

## 工具清单

工具定义在：

```text
harness/tool_manifest.json
```

底层适配器是：

```text
python3 harness/wiki_tool.py
```

这不是给普通用户手动输入的日常命令，而是给 Hermes 这类 agent runtime 绑定工具时使用的入口。

## 工具调用语义

- `wiki_ingest`：当用户说“我放了新材料，请整理”时自动调用。
- `wiki_build_index`：检索、写作、评估前自动调用。
- `wiki_search`：用户询问资料、查找证据、寻找可复用材料时调用。
- `wiki_context`：用户要求写申报书、方案、报告、总结时调用。
- `wiki_doctor`：大改目录、生成大量笔记、准备提交前调用。
- `wiki_eval`：检索质量异常或修改检索逻辑后调用。

## Hermes 系统提示词建议

把下面这段作为 Hermes 项目级 system prompt 或工作区说明：

```text
你正在维护一个 wikiR vault。用户不应该手动运行 harness 命令；你需要在后台调用 wikiR 工具。

工作目录是当前 vault 根目录。先阅读 AGENTS.md、harness/tool_manifest.json 和 90_System/prompts/。

处理新材料时，调用 wiki_ingest，再整理 01_Sources 中的源卡，必要时沉淀到 02_Notes。

回答资料查找类问题时，先调用 wiki_build_index，再调用 wiki_search。

写申报书、方案、报告、总结等复用型任务时，先调用 wiki_build_index，再调用 wiki_context，读取 90_System/context/last_context.md 后再写作。

重要修改后调用 wiki_doctor；修改检索逻辑或 eval cases 后调用 wiki_eval。

不要上传文件，不要删除原始材料，不要把检索不到的内容编造成事实。
```

## 调试方式

如果 Hermes 的工具绑定还没有配置好，开发者可以临时用 JSON 方式验证工具层：

```sh
python3 harness/wiki_tool.py '{"tool":"wiki_search","args":{"query":"本地知识库 申报书","top_k":5}}'
```

这只是调试手段，不是最终用户工作流。
