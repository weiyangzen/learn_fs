# sources/sync-backup/git-lfs/lfs/gitscanner_tree.go

Purpose: scans trees or index/listed LFS files for pointers, preserving per-path information and validating `.gitattributes` expectations.

Important APIs/types/functions: `runScanTree`, `runScanLFSFiles`, `catFileBatchTree`, `lsTreeBlobs`, `lsBlobs`, `lsFilesBlobs`, `catFileBatchTreeForPointers`, and `runScanTreeForPointers`.

Control flow: tree scans list candidate blobs via `git ls-tree` or, for Git 2.42+ LFS files, `git ls-files`, filter by size/path, decode with `PointerScanner`, and callback pointers. The pointer-validation path also reads `.gitattributes` blobs with `ObjectScanner`, constructs include/exclude filters from `gitattr.AttributePath`, records nil for non-pointers, and reports errors for files that attributes say should be LFS pointers but are plain Git blobs.

State/persistence behavior: read-only object and Git command scanning. It opens and closes object scanners and consumes channel wrappers.

Dependencies/integration: depends on `git.LsTree`, `git.LsFilesLFS`, `git.NewLsTreeScanner`, pointer scanner, object scanner, `gitattr`, and filepath filters.

Risks/test signals: by-tree validation can be expensive and must avoid deadlocks by not waiting on upstream channels after early scanner failure. Attribute macro reading is limited to top-level `.gitattributes` for macro definitions in this path. Errors are reported through callbacks for not-a-pointer cases.
