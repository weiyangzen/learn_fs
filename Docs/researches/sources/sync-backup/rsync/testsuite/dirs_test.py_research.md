## sources/sync-backup/rsync/testsuite/dirs_test.py

Purpose: focused coverage for `-d`/`--dirs`, confirming rsync copies named directories as empty directory entries without recursing.

Important APIs and control flow: uses `make_tree()` to create `FROMDIR/f0` plus nested `d1/d2/d3` files. After clearing `FROMDIR` and `TODIR`, it runs `run_rsync('-d', f'{src}/', f'{TODIR}/')`. It asserts the top-level file matches, top-level directory `d1` exists, and no child files or entries were copied inside `d1`.

State and dependencies: mutates only the standard `from` and `to` scratch trees. It depends on `rsyncfns` tree creation, file comparison, cleanup, and failure helpers.

Integration points: exercises file-list recursion control and destination creation for directory entries.

Risks and test signals: the test is intentionally narrow and low-flake. Signals are concrete filesystem assertions rather than broad directory equality, making it useful for distinguishing `-d` from recursive `-r` behavior.
