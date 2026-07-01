# 公开模板与私有 Vault 工作流

这个仓库应该作为 wikiR 的开源模板和 harness 项目维护，不应该直接作为真实个人资料库使用。

## 推荐拆分

使用两个仓库：

- 公开仓库：`wikiR`
  - 用途：架构、harness、提示词、模板、文档、评估示例。
  - 不提交真实原始材料、私人附件、生成的上下文、索引、日志或密钥。
- 私有仓库：你的真实个人 vault。
  - 用途：真实源卡、笔记、项目草稿、输出，以及可选的原始材料。
  - 可以从公开模板拉取更新。

## 公开仓库应该跟踪什么

建议跟踪：

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `.gitattributes`
- `.obsidian/app.json`
- `harness/`
- `90_System/prompts/`
- `90_System/templates/`
- `90_System/evals/`
- 不包含隐私的示例笔记或示例源卡。

建议忽略：

- `00_Inbox/materials/`
- `00_Inbox/triage/`
- `80_Attachments/`
- `90_System/index/`
- `90_System/context/`
- `90_System/logs/`
- `.env*`
- Obsidian 本地工作区状态。

## 从模板创建私有 Vault

公开仓库推送完成后，在另一个目录创建私有工作 vault：

```sh
cd /Users/tongrao/Desktop/project
git clone <PUBLIC_WIKIR_REPO_URL> wikiR-private
cd wikiR-private
git remote rename origin upstream
git remote add origin <PRIVATE_WIKIR_VAULT_REPO_URL>
git branch -M main
git push -u origin main
```

然后把 `/Users/tongrao/Desktop/project/wikiR-private` 作为 Obsidian vault 和 Hermes 工作目录。

## 同步模板更新

当公开模板有更新：

```sh
cd /Users/tongrao/Desktop/project/wikiR-private
git fetch upstream
git merge upstream/main
python3 harness/wiki.py doctor
```

如果你想保持更干净的历史，也可以用 `git rebase upstream/main` 代替 merge。

## 在私有仓库中管理真实材料

有三种合理方式。

### 方式 A：只跟踪整理后的 Markdown

保留默认 `.gitignore`。

- 原始文件只保留在本地 `00_Inbox/materials/`。
- 源卡、笔记、项目和输出进入 Git。
- 适合原始文件较大、敏感或经常替换的情况。

### 方式 B：选择性跟踪原始材料

保留默认 `.gitignore`，但在私有仓库里强制添加特定文件：

```sh
git add -f 00_Inbox/materials/example.pdf
git add -f 80_Attachments/example.png
git commit -m "Add selected private materials"
```

适合只有少量原始文件需要版本管理的情况。

### 方式 C：私有仓库跟踪全部原始材料

只在私有仓库中编辑 `.gitignore`，删除这些规则：

```gitignore
00_Inbox/materials/*
!00_Inbox/materials/.gitkeep

80_Attachments/*
!80_Attachments/.gitkeep
```

如果私有仓库会包含 PDF、Word、音频、视频或大数据文件，建议使用 Git LFS：

```sh
git lfs install
git lfs track "*.pdf" "*.doc" "*.docx" "*.xls" "*.xlsx" "*.ppt" "*.pptx" "*.mp4" "*.mov" "*.wav" "*.mp3"
git add .gitattributes
git add 00_Inbox/materials 80_Attachments
git commit -m "Track private vault materials"
```

适合私有远端可靠、存储额度足够的情况。

## 公开推送前的安全检查

在公开模板仓库中运行：

```sh
git status --short --ignored
git check-ignore -v 00_Inbox/materials/*
git check-ignore -v 90_System/context/last_context.md
git check-ignore -v 90_System/index/wiki_index.jsonl
```

只有私人材料和生成产物应该出现在 ignored 列表里。

提交前检查暂存区：

```sh
git add .
git status --short
git diff --cached --stat
git diff --cached --name-only
```

如果私人文件出现在暂存区，撤出它们：

```sh
git restore --staged <path>
```
