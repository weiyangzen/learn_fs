<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-untrack.sh -->
# sources/sync-backup/git-lfs/t/t-untrack.sh

Purpose: tests `git lfs untrack` removal of tracked patterns from attributes files, including escaping, legacy prefixes, modern prefixes, outside-repo behavior, and `GIT_WORK_TREE`.

Important APIs/functions: uses `git lfs track`, `git lfs untrack`, `.gitattributes` inspection, Git worktree/env configuration, and pattern escaping assertions.

Control flow: tracks patterns, untracks them, and compares resulting attributes. Separate cases validate outside-repo failure, removing escape sequences, prefixed legacy/modern patterns, escaped patterns in `.gitattributes`, and use from a separate `GIT_WORK_TREE`.

State and persistence: mutates `.gitattributes` and repository environment variables; no remote storage needed.

Dependencies and integration points: integrates with attributes parser/writer, path prefix normalization, escape handling, repository discovery, and Git worktree environment handling.

Risks: untrack must delete only intended rules; bad parsing can leave stale LFS filters or remove unrelated attributes.

Test signals: seven cases cover normal untrack, outside repo, escape removal, prefixed patterns, escaped attributes, and `GIT_WORK_TREE`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-untrack.sh -->
