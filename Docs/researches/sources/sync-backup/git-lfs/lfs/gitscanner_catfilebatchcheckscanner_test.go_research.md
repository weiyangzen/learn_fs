# sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatchcheckscanner_test.go

Purpose: unit tests for `catFileBatchCheckScanner` line parsing.

Important APIs/types/functions: `catFileBatchCheckScanner.Scan`, `LFSBlobOID`, `GitBlobOID`, and helper assertions.

Control flow: feeds representative cat-file lines and asserts whether each line yields a small LFS candidate, a large Git blob candidate, or neither.

State/persistence behavior: in-memory scanner only.

Dependencies/integration: supports the scan pipeline's first-stage object-size filter.

Risks/test signals: tests parser only, not live `git cat-file` subprocess behavior or channel closing.
