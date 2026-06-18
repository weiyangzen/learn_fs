<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/ai-review-comment.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/ai-review-comment.yml

Purpose: Reusable workflow that downloads AI review artifacts and posts/updates PR comments, plus reactions for manual requests or failures.

Important APIs/types/functions: `workflow_call` inputs `provider`, `result_artifact_name`, and `comment_file`; jobs `comment`, `failure-notice`, and `unauthorized-notice`. Uses `actions/download-artifact`, sparse checkout of `.github/scripts`, `post-pr-comment.js`, and GitHub reactions API.

Control flow: on successful analysis workflow runs, downloads the result artifact, reads metadata, chooses marker strategy for auto vs manual comments, and posts via shared script. Manual requests get a rocket reaction. Failed analysis runs can add a confused reaction to the triggering comment if metadata exists.

State and persistence behavior: mutates PR issue comments and reactions through GitHub API. Reads downloaded artifact files only.

Dependencies and integration points: called by `claude-review-comment.yml` and `codex-review-comment.yml` on provider workflow completion. Requires `pull-requests: write` and `issues: write`.

Risks: artifact download can fail silently due to `continue-on-error`, causing no comment. Auto marker includes workflow run id and prunes old provider auto comments, so marker bugs can leave duplicates. The unauthorized notice only logs skipped workflows.

Test signals: PR comments with provider-specific markers, obsolete comment collapse for older auto reviews, and reactions on manual trigger comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/ai-review-comment.yml -->
