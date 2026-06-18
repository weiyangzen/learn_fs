## sources/sync-backup/bup/test/ext/test-cat-file

Purpose: exercises `bup cat-file` argument validation and data/metadata extraction.

Important control flow: initializes a repo, saves a source file, checks invalid invocations and error messages, then compares `bup cat-file branch/latest/path` output to the original file. It verifies `--meta` output against `bup meta --create` while ignoring atime, and checks `--bupm` output against the raw `.bupm` object found via `git ls-tree`.

State and dependencies: uses a temp repo as both `BUP_DIR` and `GIT_DIR`, plus `dev/git-cat-tree`. It integrates with VFS path resolution, metadata encoding, and Git tree lookup.

Risks covered: rejects ambiguous flags, missing branch/revision paths, non-directory `--bupm` targets, and non-file data targets.
