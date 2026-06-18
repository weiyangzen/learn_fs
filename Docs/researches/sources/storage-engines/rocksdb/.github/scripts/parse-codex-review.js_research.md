<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/parse-codex-review.js -->
# Research: sources/storage-engines/rocksdb/.github/scripts/parse-codex-review.js

Purpose: Parses Codex CLI review artifacts and builds the standardized Codex PR comment body.

Important APIs/types/functions: exports `parseCodex({responseFile, recoveryFile, findingsFile, logFile, exitCode, meta})`; helpers `getTriggerLine`, `readIfPresent`, and `tailFile`; uses `build-ai-review-comment.js`.

Control flow: prefers a recovery file, then direct final response, then incremental `review-findings.md`, otherwise tails the execution log and emits failure text. It chooses partial/success/warning icon based on `meta.isPartial` and numeric exit code.

State and persistence behavior: only reads artifact files and returns Markdown. It caps log tail at 12k characters to avoid enormous comments.

Dependencies and integration points: invoked by shared AI review workflow after Codex auto/manual runs and optional recovery. Output is posted by the comment workflow.

Risks: missing `OPENAI_API_KEY` paths can still lead to parser output depending on generated files. Direct responses are not size-capped. Exit-code parsing defaults to failure if absent.

Test signals: generated `codex-review-comment.md`, parser fallback text when review fails, and uploaded Codex logs for diagnosis.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/parse-codex-review.js -->
