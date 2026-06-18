# sources/sync-backup/git-lfs/lfs/diff_index_scanner.go

Purpose: parses `git diff-index` output into structured entries for index scanning.

Important APIs/types/functions: `DiffIndexStatus`, status constants, `String`, `Format`, `DiffIndexEntry`, `DiffIndexScanner`, `NewDiffIndexScanner`, `Scan`, `Entry`, `Err`, and internal `scan`.

Control flow: `NewDiffIndexScanner` obtains a scanner from `git.DiffIndex`. `Scan` advances a line, parses mode/sha/status/name fields, wraps parse errors, and exposes the current entry. Rename/copy destination names are taken from a third tab-separated field.

State/persistence behavior: read-only subprocess output parser. It may trigger Git index refresh depending on caller options in `git.DiffIndex`.

Dependencies/integration: used by `gitscanner_index.go` to map modified index entries to blob SHAs and filenames.

Risks/test signals: likely bug: `if score, err := strconv.Atoi(desc[4][1:]); err != nil { entry.StatusScore = score }` sets score only when parsing failed, so valid scores are dropped. Formatting panics on unsupported verbs. No direct tests in this group cover parser edge cases.
