# wikiR 开发者说明

[English](../en/developer.md) | [README](README.md)

这份文档面向 wikiR 模板维护者。wikiR 有意保持为 vault 协议和文档项目，而不是自制 Python harness。

## 仓库策略

建议使用两个仓库：

- 公开模板仓库：维护文件夹结构、智能体工作契约、提示词、模板、示例和文档。
- 私有 vault 仓库：存放真实源卡、笔记、项目输出，以及可选的原始材料。

公开仓库不应该包含私人材料、私人附件、生成草稿、日志、密钥或 Obsidian 本地工作区状态。

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

合并后，让 Hermes 或本地 agent 检查断链、缺失 frontmatter 和无依据表述。

## Hermes 项目提示词

配置 Hermes 时，可以使用下面这段项目级说明：

```text
你正在维护一个 wikiR vault。wikiR 不提供自制 harness；请使用你自己的本地文件读取、搜索、OCR 和写作能力。

工作目录是当前 vault 根目录。先阅读 AGENTS.md 和 90_System/prompts/。

处理新材料时，读取 00_Inbox/materials 中的文件，在 01_Sources 中创建源卡，必要时把稳定知识沉淀到 02_Notes。

回答资料查找类问题时，搜索 01_Sources、02_Notes、03_Projects、04_Outputs 和相关原始材料。

写申报书、方案、报告、总结等复用型任务时，先收集证据，再基于证据写作。可行时引用源卡或笔记。

重要修改后，检查断链、YAML properties、source_path、无依据表述，以及私人材料是否被误加入暂存区。

不要上传文件，不要删除原始材料，不要把检索不到的内容编造成事实。
```

## 文档解析策略

文档解析属于运行时职责。

Hermes 或选定的本地 runtime 应该负责：

- Word 文件，包括旧版 `.doc`；
- PDF，包括可用 OCR 处理的扫描 PDF；
- 表格和演示文稿；
- 图片和附件；
- 纯文本和 Markdown。

如果解析失败，智能体应该报告失败原因，保持原始文件不动，并在必要时要求用户提供转换后或 OCR 后的文件。

## 公开推送安全检查

提交到公开仓库前运行：

```sh
git status --short --ignored
git check-ignore -v 00_Inbox/materials/*
git add -n .
```

暂存区里应该只有模板文件、提示词、文档和安全示例。

## 私有原始材料管理方式

在私有 vault 中选择一种方式：

- 保留默认 ignore，只跟踪整理后的 Markdown。
- 用 `git add -f` 选择性加入私人文件。
- 在存储和隐私条件允许时，用 Git LFS 跟踪原始材料。

不要因为某个私有 vault 需要不同的材料跟踪策略，就修改公开模板的默认安全规则。
