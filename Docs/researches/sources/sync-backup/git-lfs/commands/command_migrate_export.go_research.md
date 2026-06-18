<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_export.go -->
# sources/sync-backup/git-lfs/commands/command_migrate_export.go

Purpose: implements `git lfs migrate export`, rewriting history to replace LFS pointer blobs with real Git blobs and updating `.gitattributes` to untrack included paths.

Important APIs/types/functions: `migrateExportCommand`, `performForceCheckout`, and `trackedFromExportFilter`; `getHistoryRewriter`, `trackedFromAttrs`, `trackedToBlob`, `lfs.DecodePointer`, `gitobj.NewBlobFromFile`, `newDownloadQueue`, and `prune`.

Control flow: ensures the working copy is clean, opens object database and rewriter, requires at least one include filter, defines a blob callback that ignores `.gitattributes`, decodes LFS pointers, and replaces them with local media blobs. A root-tree callback merges adjusted `.gitattributes` lines. Before rewriting, it resolves the export remote and pre-downloads needed included objects if a download endpoint exists. After rewrite it force-checks out non-bare repos and prunes cache with recent-ref retention disabled.

State and persistence behavior: rewrites Git history and refs, downloads missing media into LFS storage, updates `.gitattributes` blobs in rewritten root trees, checks out the working tree, and prunes local LFS cache.

Dependencies/integration points: integrates migrate ref-selection/options, LFS transfer queue, object database blob/tree writing, attributes helpers from import, and shared prune logic.

Risks and test signals: risks include destructive history rewrite, needing all pointer objects locally or downloadable, `.gitattributes` union semantics preserving old lines, remote endpoint validation only when explicitly changed, and prune after rewrite. Test signals include export included patterns, excluded patterns retaining LFS attributes, missing object predownload, invalid remote, bare/non-bare checkout behavior, and object map generation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_export.go -->
