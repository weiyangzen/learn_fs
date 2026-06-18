# sources/sync-backup/git-lfs/lfs/gitscanner_index.go

Purpose: scans changed index/worktree entries for LFS pointer blobs and reports them with filename and status metadata.

Important APIs/types/functions: `scanIndex`, `revListIndex`, `indexFile`, `indexFileMap`, `FilesFor`, and `Add`.

Control flow: builds an `indexFileMap`, runs `diff-index` once for working tree and once for cached/index changes, merges unique destination SHAs, filters small blobs with batch-check, decodes pointers with cat-file batch, expands each pointer to all filenames mapped to that blob, and calls back for paths allowed by the filter.

State/persistence behavior: read-only scanning except possible Git index interaction from `DiffIndex`. The map deduplicates SHA/name pairs and is mutex-protected for goroutines.

Dependencies/integration: depends on `DiffIndexScanner`, cat-file batch helpers, filepath filters, and `WrappedPointer` status fields.

Risks/test signals: filter callback assumes `result.Pointer` is non-nil; errors from bare pointer channel are sent as a result after pointer loop but then dereferenced in the final loop path only for pointer results. The diff-index score parsing bug can affect status score consumers, though this file stores status only.
