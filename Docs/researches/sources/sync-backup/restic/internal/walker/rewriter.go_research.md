# sources/sync-backup/restic/internal/walker/rewriter.go

Purpose: recursively rewrites restic tree blobs, optionally filtering nodes, replacing failed subtrees, dropping empty directories, and computing rewritten snapshot size.

Important APIs/types/functions: function types `NodeRewriteFunc`, `FailedTreeRewriteFunc`, `NodeKeepEmptyDirectoryFunc`; `SnapshotSize`; `RewriteOpts`; `TreeRewriter`; constructors `NewTreeRewriter()` and `NewSnapshotSizeRewriter()`; method `RewriteTree()`.

Control flow: `RewriteTree()` caches by original tree ID unless disabled, loads the tree, optionally verifies stable serialization by re-saving and comparing IDs, iterates nodes, calls `RewriteNode`, recurses into directories, skips nil rewrites/null subtree rewrites, finalizes a new tree, and optionally drops empty directories.

State and persistence: `replaces` memoizes tree-ID rewrites across calls. Actual persistence happens through injected `restic.BlobSaver`.

Dependencies/integration: uses `internal/data` tree iterators/writers, `internal/restic` IDs, `debug.Log`, and `context` cancellation.

Risks: mutation of `*data.Node` returned by iterators must be safe for callers. Cache can intentionally reuse rewrites for identical subtrees, which changes path-specific rewrite semantics unless `DisableNodeCache` is set.

Test signals: rewriter tests cover order, filtering, cache behavior, size counting, empty-directory retention, unknown-field protection, and failed-tree replacement.
