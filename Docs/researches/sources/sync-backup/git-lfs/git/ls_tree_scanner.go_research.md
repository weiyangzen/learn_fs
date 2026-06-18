# sources/sync-backup/git-lfs/git/ls_tree_scanner.go

Purpose: parses NUL-delimited `git ls-tree` or compatible output into blob entries with OID, size, mode, and filename.

Important APIs/types/functions: `TreeBlob`, `LsTreeScanner`, `NewLsTreeScanner`, `TreeBlob`, `Scan`, `next`, and `scanNullLines`.

Control flow: scanner splits on NUL, separates metadata from filename at tab, parses mode and size, ignores non-blob entries or malformed lines by returning nil with the current scan state, and stores the current `TreeBlob`.

State/persistence behavior: in-memory stream parser only. No subprocess ownership is handled here.

Dependencies/integration: consumed by LFS tree scanners in `lfs/gitscanner_tree.go`.

Risks/test signals: `Err` always returns nil and malformed lines are skipped silently, so callers only see missing entries. Tests cover paths with spaces and non-ASCII characters plus benchmark basic parsing.
