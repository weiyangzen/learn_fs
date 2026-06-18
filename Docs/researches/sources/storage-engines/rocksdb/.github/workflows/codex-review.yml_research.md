<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/codex-review.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/codex-review.yml

Purpose: Provider-specific wrapper exposing Codex Code Review triggers and model inputs while using shared AI analysis.

Important APIs/types/functions: triggers on `workflow_run` of `facebook/rocksdb/pr-jobs`, same-repo `pull_request_target`, `issue_comment`, and `workflow_dispatch`. Inputs include PR number, Codex model choice (`gpt-5.5`, `gpt-5.3-codex`, `gpt-5.2-codex`) and thinking budget. Calls shared analysis with commands `/codex-review` and `/codex-query`.

Control flow: skips early pull_request_target for fork PRs; reusable analysis handles auto/manual/query branches.

State and persistence behavior: artifacts and logs are produced in the called workflow, including Codex output/recovery files.

Dependencies and integration points: pairs with `codex-review-comment.yml`, shared analysis, OpenAI API secret, and Codex CLI installation.

Risks: Codex CLI execution in shared workflow bypasses approvals/sandbox, so trust boundary depends on trigger restrictions. Model list can go stale. Workflow name coupling to PR jobs controls auto review.

Test signals: Codex review artifacts/logs and downstream PR comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/codex-review.yml -->
