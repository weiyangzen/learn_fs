# sources/sync-backup/restic/cmd/restic/cmd_dump.go

Purpose: implements `restic dump`, extracting a file to stdout or dumping a directory/snapshot subtree as tar or zip.

Important APIs/types/functions: `DumpOptions` contains snapshot filters, archive format, and target path. `splitPath` converts a cleaned POSIX path into path components. `printFromTree` recursively locates the requested node and writes file content or archive data using `dump.Dumper`. `runDump` handles CLI validation, repository access, snapshot lookup, index/tree loading, and output destination. `checkStdoutArchive` refuses archive bytes to an interactive terminal.

Control flow: validates two args and archive type, opens read lock, finds snapshot/subfolder, loads index and tree, chooses raw stdout or `--target` file writer, constructs dumper, and prints selected file or directory. Directory output checks that stdout is redirected unless a target file was specified.

State/persistence: read-only repository access; optionally creates/truncates the target output file. Raw stdout can contain binary archive data.

Dependencies/integration: `internal/dump`, `data` tree loaders, repository blob loading, terminal raw output, and snapshot filters.

Risks/test signals: target file is created before dumping succeeds, so failed dumps may leave partial files. Path handling is POSIX-style inside snapshots. Tests cover `splitPath`; full dump behavior is integration-tested elsewhere.
