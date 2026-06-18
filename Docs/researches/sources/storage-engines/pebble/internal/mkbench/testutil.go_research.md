<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testutil.go -->
# sources/storage-engines/pebble/internal/mkbench/testutil.go

Purpose: shared test helpers for mkbench parser tests.

Important APIs/functions: `filesEqual`, `copyDir`, and `maybeSkip`. `filesEqual` reads two files, normalizes CRLF to LF, and returns a unified diff as an error if contents differ. `copyDir` recursively copies a directory tree using `walkDir`. `maybeSkip` skips tests on Windows because summary fixture paths are Unix-oriented.

Control flow and state: `copyDir` creates directories with mode 0700, copies files with `io.Copy`, and follows the traversal behavior of `walkDir`, including symlinks. `filesEqual` constructs diffs through `go-difflib`.

Dependencies and integration: supports YCSB, write, and walkDir tests. Risks include preserving file mode only loosely, not handling special files beyond `walkDir` behavior, and Windows coverage being intentionally skipped. It is a test-only utility, so production risk is low.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testutil.go -->
