# sources/sync-backup/git-lfs/git/ls_tree_scanner_test.go

Purpose: verifies and benchmarks `LsTreeScanner` parsing.

Important APIs/types/functions: `NewLsTreeScanner`, `TreeBlob`, generic scanner helper assertions, and `BenchmarkLsTreeParser`.

Control flow: feeds two NUL-delimited ls-tree records and asserts OIDs and filenames, including a filename containing spaces and a non-ASCII character. The benchmark repeatedly scans the same sample.

State/persistence behavior: in-memory only.

Dependencies/integration: supports confidence for `gitscanner_tree.go` tree-walking code.

Risks/test signals: narrow coverage; does not test malformed lines, non-blob entries, size/mode parsing failures, or scanner buffer limits.
