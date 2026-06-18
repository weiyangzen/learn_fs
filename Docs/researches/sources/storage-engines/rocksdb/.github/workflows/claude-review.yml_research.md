<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/claude-review.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/claude-review.yml

Purpose: Provider-specific wrapper exposing Claude Code Review triggers and inputs while delegating implementation to shared AI analysis.

Important APIs/types/functions: triggers on `workflow_run` of `facebook/rocksdb/pr-jobs`, same-repo `pull_request_target`, `issue_comment`, and `workflow_dispatch`. Inputs include PR number, Claude model choice, and thinking budget. Calls `ai-review-analysis.yml` with provider `claude`, commands `/claude-review` and `/claude-query`, default model `claude-opus-4-6`, classifier/recovery `claude-sonnet-4-6`.

Control flow: skips fork PRs on the early `pull_request_target` path and otherwise delegates to reusable workflow.

State and persistence behavior: state is produced by the called reusable workflow as artifacts/logs, not directly here.

Dependencies and integration points: pairs with `claude-review-comment.yml`, `ai-review-analysis.yml`, and the PR jobs workflow name.

Risks: hardcoded model choices and workflow names can drift. Same-repo condition protects early trigger, while fork reviews rely on workflow_run fallback.

Test signals: dispatch/manual/comment/auto triggers produce Claude review result artifacts and downstream comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/claude-review.yml -->
