<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/claude-review-comment.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/claude-review-comment.yml

Purpose: Provider-specific wrapper that posts Claude review comments using the shared AI comment workflow.

Important APIs/types/functions: triggered by completed workflow `Claude Code Review`; job `review-comment` calls `./.github/workflows/ai-review-comment.yml` with provider `claude`, artifact `claude-review-result`, and comment file `claude-review-comment.md`.

Control flow: delegates all logic to the reusable comment workflow and inherits secrets.

State and persistence behavior: no direct state beyond delegated comment/reaction mutations.

Dependencies and integration points: pairs with `claude-review.yml` and shared `ai-review-comment.yml`.

Risks: workflow name coupling means renaming the analysis workflow breaks trigger matching. Permissions must include both pull request and issue write.

Test signals: Claude analysis completion results in posted or updated Claude PR comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/claude-review-comment.yml -->
