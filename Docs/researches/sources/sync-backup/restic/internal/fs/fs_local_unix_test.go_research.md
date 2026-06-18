# sources/sync-backup/restic/internal/fs/fs_local_unix_test.go

Purpose: Unix-only extension of local metadata tests for sockets and FIFOs.

Important APIs: `TestFSLocalMetadataUnix`.

Control flow and state: Creates a Unix domain socket by binding a syscall socket and creates a FIFO via `mkfifo`, then reuses `runFSLocalTestcase`.

Dependencies and integration: Exercises `nodeTypeFromFileInfo`, Unix stat extraction, and local metadata-only open for special node types.

Risks: Device nodes are intentionally not tested because they require root.

Test signals: Confirms backup metadata recognizes socket and FIFO node types on Unix.
