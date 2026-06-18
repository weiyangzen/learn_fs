<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/clang-tidy-comment.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/clang-tidy-comment.yml

Purpose: Posts or updates a PR comment containing clang-tidy results from the separate clang-tidy workflow.

Important APIs/types/functions: triggered by completed `workflow_run` for workflow `clang-tidy`; job downloads `clang-tidy-result`, reads `clang-tidy-comment.md` and `pr_number.txt`, and calls `post-pr-comment.js` with marker `<!-- clang-tidy-bot -->`.

Control flow: only handles pull_request-origin workflow runs. If artifact download succeeds and files exist, it posts/updates the comment.

State and persistence behavior: mutates PR comments through GitHub API; downloaded artifacts are temporary.

Dependencies and integration points: pairs with `clang-tidy.yml`; requires sparse checkout of scripts and `pull-requests: write`.

Risks: if artifact is missing or the workflow was a push run, no comment is posted. Uses one stable marker, so every new clang-tidy result replaces the old bot comment.

Test signals: PR comment appears or updates after clang-tidy workflow completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/clang-tidy-comment.yml -->
