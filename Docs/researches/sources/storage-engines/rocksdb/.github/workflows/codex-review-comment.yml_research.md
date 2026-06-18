<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/codex-review-comment.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/codex-review-comment.yml

Purpose: Provider-specific wrapper that posts Codex review comments through the shared AI comment workflow.

Important APIs/types/functions: triggered by completed `Codex Code Review`; calls `ai-review-comment.yml` with provider `codex`, artifact `codex-review-result`, and comment file `codex-review-comment.md`.

Control flow: all logic is delegated to the reusable comment workflow.

State and persistence behavior: no direct local state; delegated workflow mutates PR comments/reactions.

Dependencies and integration points: pairs with `codex-review.yml`.

Risks: trigger depends on exact analysis workflow name. Permission scope must allow issue and pull-request writes.

Test signals: Codex result artifacts become PR comments with Codex markers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/codex-review-comment.yml -->
