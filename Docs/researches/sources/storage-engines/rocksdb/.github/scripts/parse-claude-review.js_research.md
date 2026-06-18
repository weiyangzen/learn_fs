<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/parse-claude-review.js -->
# Research: sources/storage-engines/rocksdb/.github/scripts/parse-claude-review.js

Purpose: Parses Claude Code execution logs and converts them into a standardized AI review/comment Markdown body.

Important APIs/types/functions: exports `parseClaude({executionFile, conclusion, meta})`; internal `getTriggerLine` chooses manual/auto early/auto late text; `getLastAssistantText` recovers substantial assistant text from logs; uses `build-ai-review-comment.js`.

Control flow: reads and parses a JSON execution log, finds the `type === 'result'` message, handles success, generic error, `error_max_turns`, partial fallback, empty output, and parse exceptions, then builds a comment with Claude-specific footer commands.

State and persistence behavior: reads the execution file only and returns text; it does not write comments itself.

Dependencies and integration points: called by `ai-review-analysis.yml` in Claude auto/manual paths after `anthropics/claude-code-base-action`. The produced file is uploaded and later posted by `ai-review-comment.yml`.

Risks: assumes the execution log is a JSON array with Claude action message schema. It truncates recovered text to 50k chars but successful results are not truncated here. It embeds generated output directly into PR comments.

Test signals: successful parser step writes `claude-review-comment.md`; failure modes show parse/error messages in the posted artifact.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/parse-claude-review.js -->
