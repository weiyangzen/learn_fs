# sources/sync-backup/git-lfs/lfs/gitscanner_log.go

Purpose: scans `git log -p` output for LFS pointer additions or deletions, supporting unpushed, stashed, and previous-version scans.

Important APIs/types/functions: `LogDiffDirection`, `logLfsSearchArgs`, `scanUnpushed`, `scanStashed`, `parseScannerLogOutput`, `logPreviousSHAs`, `logScanner`, `newLogScanner`, `Scan`, `finishLastPointer`, and `setFilename`.

Control flow: Git log commands are constructed with no external diff/textconv, no color, `-G oid sha256:`, patch context, and a custom commit header. `parseScannerLogOutput` drains stderr concurrently, scans pointers, waits on the command, and calls back. `logScanner` tracks commit/file diff boundaries, collects pointer lines from either additions or deletions plus context, decodes complete pointer blocks, unquotes filenames, and applies filters.

State/persistence behavior: read-only Git log subprocess scanning. Stash scan runs two log passes for merge-parent semantics.

Dependencies/integration: depends on `git.Log`, `DecodePointer`, filepath filters, subprocess buffered command, and tracer logging.

Risks/test signals: parser is regex- and diff-format-sensitive. `setFilename` calls `s.Filter.Allows(name)` without nil guard, so callers must provide a non-nil filter or rely on wrapper defaults elsewhere. Stash scan ignores `git log` errors when no stash exists. Tests outside this listed file cover log scanner additions/deletions.
