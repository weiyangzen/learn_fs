# sources/test-tools/unionmount-testsuite/tests/rename-mass-dir.py

Purpose: validates mass circular renames of directories, first empty and then populated. It is aimed at overlay directory rename, whiteout/opaque handling, and child preservation.

Important APIs and functions: exports five `subtest_*` functions using `ctx.no_dir()`, `ctx.mkdir()`, `ctx.rename()`, `ctx.rmdir()`, `ctx.open_file()`, and `ctx.unlink()`.

Control flow: subtests 1 and 2 create empty directories, rotate one gap around a seven-name ring, and remove survivors. Subtests 3 to 5 repeat with a file `a` in each directory, compute final content order, read each payload, then unlink children and remove directories.

State and persistence: directory dentries and child files persist across multiple renames. The content check reconstructs expected order from `iter_count`, ring cycle length, and final gap.

Dependencies and integration: depends on harness directory factories and filesystem support for directory rename. It integrates with overlay lower/upper state through `ctx.rename` and `ctx.rmdir`.

Risks: the arithmetic for expected payload order is dense and can fail if `iter_count` or `ring_size` changes without updating reasoning. Directory renames across union layers are high-risk operations.

Test signals: successful renames, expected absent gap, preserved child file contents, and clean removal of every surviving directory.
