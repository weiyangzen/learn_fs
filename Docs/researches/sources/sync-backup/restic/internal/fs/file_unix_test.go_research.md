# sources/sync-backup/restic/internal/fs/file_unix_test.go

Purpose: Unix-only regression test for safe directory reads on FIFOs.

Important APIs: `TestReaddirnamesFifo`.

Control flow and state: Creates a FIFO with `mkfifo`, calls `Readdirnames(NewLocal(), fifo, 0)`, and asserts the error is `ENOTDIR`.

Dependencies and integration: Covers `Readdirnames`, `O_DIRECTORY`, local `OpenFile`, and Unix `mkfifo`.

Risks: Focused on blocking avoidance; it does not test normal directory reads, which are covered elsewhere.

Test signals: Confirms opening a FIFO as a directory fails promptly rather than blocking on FIFO read behavior.
