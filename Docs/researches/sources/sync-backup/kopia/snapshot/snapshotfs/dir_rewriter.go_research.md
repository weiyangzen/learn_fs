# sources/sync-backup/kopia/snapshot/snapshotfs/dir_rewriter.go

Purpose: recursively rewrites snapshot directory trees, allowing callers to replace, remove, keep, or stub entries and then write new directory manifests.

Important APIs/types/functions: `RewriteDirEntryCallback`, `RewriteFailedEntryCallback`, `UnreadableDirEntryReplacement`, `DirRewriterOptions`, `DirRewriter`, `RewriteSnapshotManifest`, `RewriteKeep`, `RewriteAsStub`, `RewriteFail`, `RewriteRemove`, and `NewDirRewriter`.

Control flow: entries are keyed by SHA1 of JSON metadata in a `bigmap` cache. Rewrites may run through a workshare pool. Directory replacements are recursively opened, read, children rewritten, rebuilt with `DirManifestBuilder`, and persisted with `WriteDirManifest`; unreadable directories go through the configured failure callback.

State and persistence: writes new directory objects and optional stub file objects to the repository, and mutates `man.RootEntry` when changed. Cache and worker pool are closed explicitly.

Dependencies and integration points: integrates with repository object writers, metadata compression policy, snapshot manifests, and maintenance/repair workflows.

Risks and test signals: cache keys ignore parent path, so identical metadata entries share rewritten output. Failure callback choice controls whether corrupt subtrees are kept, removed, stubbed, or fatal. Stub creation depends on effective global policy.
