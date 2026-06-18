# sources/sync-backup/git-lfs/git/githistory/rewriter.go

Purpose: rewrites Git history by applying blob and tree callbacks across selected commits, preserving topology, optionally filtering paths, writing an object map, and updating refs.

Important APIs/types/functions: `Rewriter`, `RewriteOptions`, `BlobRewriteFn`, `TreePreCallbackFn`, `TreeCallbackFn`, `WithFilter`, `WithLogger`, `NewRewriter`, `Rewrite`, `rewriteTree`, `rewriteBlob`, `commitsToMigrate`, `refsToMigrate`, `scannerOpts`, `cacheEntry`, and `cacheCommit`.

Control flow: `Rewrite` obtains commits from `git rev-list` in reverse topological order, rewrites each commit tree recursively, rewrites parent IDs through the commit cache or preserves original parents outside the migration range, writes changed commits, records object-map rows, and optionally calls `refUpdater`. `rewriteTree` pre-callbacks each tree, skips disallowed blobs and symlinks, reuses cached path/OID entries, rewrites blobs or subtrees, post-callbacks the assembled tree, and writes changed trees.

State/persistence behavior: writes new blobs, trees, commits, optional object-map files, and optionally refs/tag objects. In-memory caches map old entries and commits to rewritten values; a mutex guards those maps.

Dependencies/integration: depends on `gitobj`, `git.NewRevListScanner`, `filepathfilter`, `tasklog`, and `refUpdater`. It is a core integration point for migration commands that need to rewrite repository history.

Risks/test signals: rewriting Git history is high blast-radius. Risks include callback errors, incorrectly preserving partial migration parents, cache key mistakes for same-content different paths, symlink handling, filter semantics, and ref update failures after objects are written. Tests cover linear history, octopus merges, packed objects, repeated and identical blobs, filters with cache, tree callbacks adding entries, callback order/errors, partial migrations, ref updates, and filter identity.
