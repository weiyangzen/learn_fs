<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/util_test.go -->
# sources/storage-engines/pebble/internal/mkbench/util_test.go

Purpose: verifies `walkDir` traverses mkbench fixture data, including the symlinked fixture path, with the expected number of entries.

Important APIs/functions: `TestWalkDir` and constant `wantCount = 97`.

Control flow and state: the test calls `maybeSkip`, then for each path in `dataDirPaths` invokes `walkDir`, appending every relative path reported to `paths`. It asserts no error and exact path count.

Dependencies and integration: depends on shared `dataDirPaths` from `ycsb_test.go` and `testify/require`. It gives signal for symlink following and fixture shape. Risks not covered include ordering, path content, symlink cycles, errors from the handler, and non-directory special file behavior. The hard-coded count will need updates when fixtures change.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/util_test.go -->
