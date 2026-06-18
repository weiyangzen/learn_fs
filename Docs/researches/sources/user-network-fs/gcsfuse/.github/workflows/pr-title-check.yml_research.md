## sources/user-network-fs/gcsfuse/.github/workflows/pr-title-check.yml

Purpose: Enforces Conventional Commit style PR titles and manages a sticky explanatory comment.

Important APIs/types/functions: triggers on `pull_request_target` opened/edited. Uses `amannn/action-semantic-pull-request@v5`, then `marocchino/sticky-pull-request-comment@v2` to post or delete a `pr-title-lint-error` comment.

Control flow: validate title, if error output exists post/update a sticky comment with details; if no error, delete the sticky comment.

State and persistence: writes/deletes PR comments. Does not modify repository files.

Dependencies and integration points: relies on GitHub token, semantic-pull-request action, and repository PR title policy.

Risks: `pull_request_target` has elevated context; this workflow does not checkout or run PR code, limiting exposure. The visible message includes emoji/non-ASCII but source file handles it. Action versions should be periodically reviewed.

Test signals: PR check result and sticky comment behavior when editing titles.
