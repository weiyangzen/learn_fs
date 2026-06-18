# sources/sync-backup/restic/cmd/restic/cmd_dump_test.go

Purpose: unit tests for dump path splitting.

Important tests: `TestDumpSplitPath` verifies empty, relative, nested, root, and absolute path inputs produce expected component arrays.

State/dependencies: no repository access; uses `splitPath` and `rtest.Equals`.

Risks/test signals: protects a small but important helper used to locate nodes in snapshot trees. It does not validate archive generation or file content output.
