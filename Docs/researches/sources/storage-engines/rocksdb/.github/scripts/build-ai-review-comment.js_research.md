<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/build-ai-review-comment.js -->
# Research: sources/storage-engines/rocksdb/.github/scripts/build-ai-review-comment.js

Purpose: Shared Node helper that formats AI review output into a consistent Markdown PR comment.

Important APIs/types/functions: exports `buildAiReviewComment({icon, headerTitle, triggerLine, responseBody, footerLines})`, returning a joined Markdown string with heading, trigger line, body, separators, and an expandable details footer.

Control flow: pure formatting only; it builds an array of lines and joins with newline characters.

State and persistence behavior: no state, filesystem, or network access.

Dependencies and integration points: required by `parse-claude-review.js` and `parse-codex-review.js`, which are invoked from `ai-review-analysis.yml`.

Risks: does not sanitize body/footer markdown, which is acceptable for generated comments but means callers control all rendered content. Uses an info emoji in the summary, so consumers expecting ASCII-only output should not reuse it unchanged.

Test signals: indirect through parser scripts and posted PR comment shape; there is no direct unit test for this helper.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/build-ai-review-comment.js -->
