# sources/test-tools/kdevops/scripts/workflows/fstests/find-common-failures.sh

## Purpose
Finds common fstests expunge entries across per-section expunge files and appends them to `all.txt`.

## Important APIs
`usage()`, `parse_args()`, and `print_all_common_expunges()` implement CLI handling and output. `--lazy-baseline` changes the definition of common from present in all files to present in at least two files.

## Control flow
The script validates an expunge directory, collects all files except `all.txt`, loops over each test token from each file, counts how many files contain it, appends qualifying entries to a temporary list, merges that into `$DIR/all.txt`, sorts, and deduplicates.

## State and persistence
Mutates `$DIR/all.txt`, creating or extending it. Uses `mktemp` for intermediate state.

## Dependencies and integration
Depends on `find`, `grep`, `awk`, `sort`, `uniq`, `mktemp`. Used by `lazy-baseline.sh` and manual expunge maintenance.

## Risks and test signals
Grep patterns are unescaped test names, so regex metacharacters could overmatch. Nested loops are quadratic in number of files and entries. Test with known expunge fixtures in strict and lazy modes.
