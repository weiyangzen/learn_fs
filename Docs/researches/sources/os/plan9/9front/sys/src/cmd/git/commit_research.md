# File Research: sources/os/plan9/9front/sys/src/cmd/git/commit

rc script for creating, revising, and partially selecting commits.

Key responsibilities:
- Finds the active branch/ref and handles initial commits.
- Builds parent lists for normal, revised, and merge commits.
- Creates or edits commit messages and strips comments/extra blank lines.
- Collects changed files from explicit paths, merge state, or git walk.
- Supports partial commit hunk selection by building and applying a temporary patch in ramfs.
- Calls `git/save` and updates branch/HEAD plus `.git/INDEX9`.

Important behavior:
- Defaults editor from `git/conf core.editor`, then `$editor`, then `hold`.
- `-m` supplies a message, `-e` edits, `-r` revises, and `-p` commits selected hunks.
- Removes `.git/merge-parents` after successful update.

Notable risks:
- Partial hunk path uses bind mounts and patch application; failure handling is intentionally conservative.
