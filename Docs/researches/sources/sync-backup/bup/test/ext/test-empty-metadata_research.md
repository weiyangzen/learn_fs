## sources/sync-backup/bup/test/ext/test-empty-metadata

Purpose: tests VFS/metadata behavior when `.bupm` entries are empty or missing for non-directories.

Important control flow: saves files and a fifo, checks normal `bup ls -l`, then rewrites the tree’s `.bupm` with selected entries cleared via `dev/clear-bupm-entries`. It verifies lost metadata shows restrictive permissions and unknown owner/time, then restores under `umask 0` and checks filesystem modes.

State and dependencies: directly manipulates Git tree objects and branch refs inside the temp repo. Depends on `bup meta`, `bup join`, `git hash-object/mktree/commit-tree`, and restore.

Risks covered: lost metadata must not become overly permissive; special files with lost metadata become safe regular placeholders.
