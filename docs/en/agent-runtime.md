# Agent Runtime Integration

The normal wikiR workflow should not require users to open a terminal and run Python commands. The intended flow is:

1. The user makes a natural-language request in Obsidian, Hermes, or another local agent interface.
2. Hermes decides which wikiR tools are needed based on `AGENTS.md`.
3. Hermes calls the tools defined in `harness/tool_manifest.json`.
4. The tool layer maintains source cards, indexes, retrieval context, and eval results in the background.
5. The user only sees curated notes, retrieved evidence, drafts, or validation results.

## Tool Manifest

Tool definitions live in:

```text
harness/tool_manifest.json
```

The low-level adapter is:

```text
python3 harness/wiki_tool.py
```

This adapter is meant for agent-runtime integration. It is not the daily user interface.

## Tool Semantics

- `wiki_ingest`: called when the user says new materials have been added and should be curated.
- `wiki_build_index`: called before retrieval, writing, or evaluation.
- `wiki_search`: called when the user asks to find materials, evidence, or reusable fragments.
- `wiki_context`: called before drafting proposals, reports, plans, summaries, or other reuse-heavy outputs.
- `wiki_doctor`: called after large changes or before commits.
- `wiki_eval`: called after retrieval changes or when retrieval quality looks wrong.

## Suggested Hermes System Prompt

Use this as the Hermes project-level system prompt or workspace instruction:

```text
You are maintaining a wikiR vault. The user should not manually run harness commands; you must call wikiR tools in the background.

The working directory is the vault root. First read AGENTS.md, harness/tool_manifest.json, and 90_System/prompts/.

When processing new materials, call wiki_ingest, then curate the generated source cards in 01_Sources and promote durable knowledge to 02_Notes when useful.

For material lookup questions, call wiki_build_index and then wiki_search.

For proposals, plans, reports, summaries, and other reuse-heavy writing tasks, call wiki_build_index and then wiki_context. Read 90_System/context/last_context.md before drafting.

After important edits, call wiki_doctor. After retrieval logic or eval-case changes, call wiki_eval.

Do not upload files, do not delete raw materials, and do not invent facts that were not retrieved or otherwise provided.
```

## Debugging

If the Hermes tool binding has not been configured yet, developers can validate the tool layer with JSON:

```sh
python3 harness/wiki_tool.py '{"tool":"wiki_search","args":{"query":"local knowledge base proposal","top_k":5}}'
```

This is a debugging path, not the final user workflow.
