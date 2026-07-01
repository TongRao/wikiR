# Agent Operating Protocol

wikiR is meant to be maintained by a local agent runtime such as Hermes. It does not ship a custom document parser, indexer, or Python harness.

## Runtime Responsibilities

The agent runtime should provide or delegate:

- file reading for Markdown, PDF, Word, spreadsheets, and plain text;
- OCR or conversion when a file is scanned or not directly readable;
- vault-wide search over notes and raw materials;
- Markdown editing;
- link and metadata inspection;
- local-only execution unless the user explicitly allows network use.

## Normal Flow

1. The user makes a natural-language request in Obsidian, Hermes, or another local interface.
2. The agent reads `AGENTS.md` and the relevant prompt profile in `90_System/prompts/`.
3. The agent reads raw materials or existing notes directly with runtime-native capabilities.
4. The agent creates source cards, durable notes, project drafts, or outputs using `90_System/templates/`.
5. The agent reports evidence used and any extraction or search limitations.

## Material Curation

When the user adds material to `00_Inbox/materials/`, the agent should:

1. read each new file with the best available local method;
2. create one source card per meaningful source in `01_Sources/`;
3. preserve `source_path`, extraction status, and short excerpts;
4. extract reusable facts, claims, constraints, examples, and writing fragments;
5. promote only stable cross-project knowledge into `02_Notes/`;
6. leave raw files untouched unless the user explicitly approves moving or deleting them.

## Search and Writing

For reuse-heavy tasks such as proposals, plans, reports, and summaries, the agent should:

1. search `01_Sources/`, `02_Notes/`, `03_Projects/`, `04_Outputs/`, and relevant raw materials;
2. read the strongest matches directly;
3. draft from evidence rather than memory alone;
4. cite source cards or notes where practical;
5. list missing materials or extraction failures before filling gaps.

## Failure Handling

If the runtime cannot read a file:

- do not invent the content;
- record the failure in the source card or response;
- ask for a converted or OCRed version when needed;
- keep the raw file in place.

For example, a scanned PDF may require OCR, and legacy `.doc` files may require conversion to `.docx` or runtime-specific document support.
