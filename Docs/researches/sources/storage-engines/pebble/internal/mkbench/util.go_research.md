<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/util.go -->
# sources/storage-engines/pebble/internal/mkbench/util.go

Purpose: common mkbench utility functions for JSON formatting and recursive directory walking with symlink handling.

Important APIs/functions: `prettyJSON(v interface{}) []byte` and `walkDir(dir, handleFn)`.

Control flow and state: `prettyJSON` marshals with tab indentation and terminates the process with `log.Fatal` on marshal errors. `walkDir` wraps `filepath.Walk`; for non-regular/non-directory entries it calls `os.Stat`, and if the target is a directory it recursively walks that symlinked directory. For every accepted entry it computes the relative path and calls `handleFn`.

Dependencies and integration: used by YCSB and write loaders and by tests. It integrates with fixtures that include symlinked directories. Risks include potential cycles through symlinked directories, swallowed errors from the recursive symlink walk (`_ = filepath.Walk(...)`), process exit from `prettyJSON`, and deprecated `filepath.Walk` style. Tests validate fixture traversal count across real and symlinked test data.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/util.go -->
