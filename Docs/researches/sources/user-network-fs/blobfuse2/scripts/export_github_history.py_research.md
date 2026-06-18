<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/export_github_history.py -->
# sources/user-network-fs/blobfuse2/scripts/export_github_history.py

## Purpose
Exports GitHub issues, pull requests, issue comments, PR reviews, and PR review comments into JSONL files suitable for Azure AI Search indexing.

## Important APIs, Types, and Functions
Configuration uses `OWNER`, `REPO`, `GITHUB_TOKEN`, `OUT_DIR`, and `STATE_FILE`. `_headers` builds GitHub headers. `_request_json` handles rate limits and transient 5xx retries. `_paginate` walks paginated REST responses. `_stable_id` creates deterministic SHA-256 document IDs. `export` orchestrates issue/PR listing, thread document writing, comment/review export, flushing, and incremental state update.

## Control Flow and State
`state.json` stores the latest `updated_at` cursor. First/full runs open output files in write mode; incremental runs append when all prior outputs exist. The GitHub issues endpoint provides both issues and PRs. For PRs, the script additionally fetches reviews and diff comments. Files are flushed after each thread to preserve partial progress.

## Dependencies and Integration Points
Depends on `requests` and GitHub REST API. Outputs `threads_issues_prs.jsonl`, `issue_pr_comments.jsonl`, `pr_reviews.jsonl`, and `pr_review_comments.jsonl` under `OUT_DIR`.

## Risks and Edge Cases
Incremental append can duplicate documents, relying on downstream stable IDs for upsert behavior. The PR reviews endpoint has no since filter, so filtering by `submitted_at` can miss edits to older reviews. The issue list sorted desc by updated time stops only when pagination returns empty, which is correct but can be slow. API errors abort the export after partial writes.

## Test Signals
Console counts and `[ok]` messages plus valid JSONL files are the main signals. A useful validation is line-by-line JSON parsing and checking stable ID uniqueness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/export_github_history.py -->
