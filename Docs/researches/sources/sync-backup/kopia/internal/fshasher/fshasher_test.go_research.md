# sources/sync-backup/kopia/internal/fshasher/fshasher_test.go

Purpose: verifies that filesystem tree hashes are stable for equivalent trees and change for structural, content, and permission differences.

Important APIs/types/functions: `Hash`, `mockfs.NewDirectory`, `AddFile`, `AddDir`, `testlogging.Context`, and `testify/require`.

Control flow: the test builds a mock root with a file and directory, hashes it, mutates the tree by adding another directory, and asserts the root hash changes. It then compares two equivalent subdirectories, adds an extra file to one, and checks inequality. Finally it creates directories/files with differing permission attributes and asserts different hashes.

State/persistence behavior: all filesystem state is in-memory `mockfs`. The test targets deterministic serialization rather than durable files.

Dependencies/integration: validates integration between `fshasher`, `mockfs`, Kopia `fs` interfaces, and test logging context.

Risks/test signals: the final file-permission scenario appears to construct a directory similar to a previous one and primarily catches metadata sensitivity. The test does not cover symlink targets, timestamp truncation, or file read errors.
