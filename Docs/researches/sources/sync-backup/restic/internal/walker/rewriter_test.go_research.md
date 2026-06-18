# sources/sync-backup/restic/internal/walker/rewriter_test.go

Purpose: validates tree-rewrite behavior using in-memory tree maps.

Important APIs/types/functions: helper factories `checkRewriteItemOrder`, `checkRewriteSkips`, `checkIncreaseNodeSize`; tests `TestRewriter`, `TestSnapshotSizeQuery`, `TestRewriterKeepEmptyDirectory`, `TestRewriterFailOnUnknownFields`, and `TestRewriterTreeLoadError`.

Control flow: tests build source and expected trees with helpers from `walker_test.go`, run `RewriteTree`, and compare resulting root IDs. Cache-specific cases demonstrate that identical subtree IDs are rewritten once unless caching is disabled.

State and persistence: in-memory `data.TestWritableTreeMap` acts as both loader and saver.

Dependencies/integration: depends on restic test helpers, `data` tree hashing, and `slices.Values` for failed-tree replacement.

Risks: root-ID comparisons provide strong structural checks but can be opaque when failures occur, hence dump logging.

Test signals: strong coverage for file/dir exclusion, node mutation, cache semantics, snapshot-size accumulation, empty-directory policies, serialization-loss detection, and missing-tree recovery hooks.
