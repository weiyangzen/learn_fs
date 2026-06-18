# sources/sync-backup/restic/internal/archiver/tree_saver_test.go

Purpose: Unit tests for concurrent `treeSaver` behavior.

Important APIs and types: `mockSaver` implements async blob saving by hashing buffers in goroutines. `setupTreeSaver` creates a context, errgroup, tree saver, and shutdown function. Tests include `TestTreeSaver`, `TestTreeSaverError`, and `TestTreeSaverDuplicates`.

Control flow and state: Success tests enqueue many tree nodes and consume futures. Error tests inject a failing child future at different positions and assert shutdown returns that error. Duplicate tests submit two children with the same name and either identical or different metadata, expecting identical duplicates to be tolerated and non-identical duplicates to fail.

Dependencies and integration: Uses `data.Node`, `restic.Hash`, `errgroup`, `runtime.NumCPU`, and package `futureNode` helpers.

Risks and test signals: The tests protect worker shutdown semantics, error propagation from child futures, and the special duplicate-node behavior required during tree construction.
