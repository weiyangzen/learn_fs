## sources/sync-backup/rsync/testsuite/link-dest-pathroot_test.py

Purpose: functional regression test for relative `--link-dest=../01` against a daemon module configured with `path = /`.

Important APIs and control flow: creates sibling basis `base/01` and source `src`, copies identical `f.dat` to the basis, serves a root module, and addresses `base` through the module using its absolute path without the leading slash. It pushes to `root/<base_rel>/00/` with `--link-dest=../01`, allows rc `0` or `23`, then requires the destination file to be hard-linked to the basis or reports an expected failure with `test_xfail`.

State and dependencies: fixed daemon port 12931, daemon config, `shutil.copy2`, inode comparison.

Integration points: covers daemon receiver alt-basis re-anchoring when module path length is zero.

Risks and test signals: intentionally XFAILs on platforms that cannot safely honor `..` via `openat2`/`RESOLVE_BENEATH`. Passing signal is inode identity with the sibling basis.
