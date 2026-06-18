# sources/sync-backup/git-lfs/lfs/gitscanner_refs.go

Purpose: implements ref/range scanning pipeline for unique Git objects and optional per-tree scanning.

Important APIs/types/functions: `nameMap`, `lockableNameSet`, `scanRefsToChan`, `scanRefsToChanSingleIncludeExclude`, `scanRefsToChanSingleIncludeMultiExclude`, `scanRefsByTree`, and `revListShas`.

Control flow: `revListShas` runs `git.NewRevListScanner`, records object names by SHA, and streams SHA strings. `scanRefsToChan` filters small blobs with batch-check, reports lockable large blobs, decodes pointers, assigns names from the map, applies the scanner filter, and forwards pointer errors. `scanRefsByTree` scans each commit/tree SHA concurrently using `runScanTreeForPointers`.

State/persistence behavior: read-only Git scans with goroutines and channels. Name maps are mutex-protected.

Dependencies/integration: ties together `GitScanner`, rev-list scanner, cat-file batch stages, lockable callbacks, and filepath filters.

Risks/test signals: unique-object mode loses duplicate path information by design, while by-tree mode is more expensive and concurrent. Callback/filter nil handling depends on scanner initialization. Errors can arrive from multiple asynchronous stages.
