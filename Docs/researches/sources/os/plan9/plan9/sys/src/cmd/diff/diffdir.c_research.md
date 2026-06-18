# File Research: sources/os/plan9/plan9/sys/src/cmd/diff/diffdir.c

Directory comparison layer for `diff`.

`scandir` opens a directory, reads all entries with `dirreadall`, copies names into a NULL-terminated string array, sorts names with `qsort`, and returns an empty list on open failure. `isdotordotdot` filters `.` and `..`.

`diffdir` walks the two sorted name arrays in merge order. Missing names produce `Only in ...` output in normal and `-n` modes. Matching names are joined with their parent paths using `mkpathname` and recursively passed to `diff`.

Integration points: called from `main.c` when both operands are directories and recursion/level rules allow.

Risks and notes: it holds whole directory listings in memory. Open failure is treated as an empty directory after printing an error, which can suppress hard failure in multi-file mode.
