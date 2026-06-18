## sources/sync-backup/rsync/testsuite/link-dest-module-escape_test.py

Purpose: security regression guard ensuring a daemon receiver does not honor a relative `--link-dest` path that climbs outside the module root.

Important APIs and control flow: creates a daemon module `mod/00`, a source tree, and an outside sibling containing an identical `f.dat`. It starts a test daemon with writable module `bak` and pushes with `--link-dest=../../OUTSIDE` to `bak/00/`. Return code `0` or `23` is allowed. It then asserts the destination exists but is not hard-linked to the outside secret file.

State and dependencies: uses daemon config helpers, `start_test_daemon`, fixed port 12916, `make_data_file`, and inode comparison.

Integration points: validates confined resolver behavior for daemon alt-basis dirs and module boundary enforcement.

Risks and test signals: same-inode detection catches information leak/cross-module hard-link regressions. Platform resolver differences are tolerated by allowing rc 23.
