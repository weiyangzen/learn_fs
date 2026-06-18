# sources/test-tools/unionmount-testsuite/tests/rename-move-dir.py

Purpose: covers moving directories between parent directories, including empty, populated, newly created, and nested directory cases. It targets overlay directory relocation correctness across lower and upper parents.

Important APIs and functions: twelve `subtest_*` functions use `ctx.empty_dir()`, `ctx.non_empty_dir()`, `ctx.no_dir()`, `ctx.mkdir()`, `ctx.rename()`, `ctx.open_dir()`, and `ctx.open_file()`.

Control flow: early subtests move existing empty/populated directories into another directory and verify old names vanish. Middle cases rename a directory or child before moving it, then verify child locations. Later cases create new directories under lower ancestors and move leaves or branches into lower-name targets.

State and persistence: directory tree topology is the key state. Child files `a` and nested `pop/b` are used as durable signals that descendants moved with their parent and that removed source paths stay hidden.

Dependencies and integration: relies on harness fixtures for empty and non-empty directories and on overlayfs support for redirect/rename of directories. It integrates with tests for whiteouts and copy-up through expected `ENOENT`.

Risks: uses trailing slashes on many paths, so path normalization differences can influence errno. Cross-directory rename of populated directories is one of the more sensitive overlay operations.

Test signals: old source names must fail with `ENOENT`, destination dirs must open, and expected child files must be found in exactly the new locations.
