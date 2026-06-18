## sources/sync-backup/rsync/testsuite/protected-regular_test.py

Purpose: Linux-specific guard that `--inplace` can write to a protected regular file in a world-writable sticky directory when `fs.protected_regular` is enabled.

Important APIs and control flow: checks `/proc/sys/fs/protected_regular`, skips if unavailable or disabled, creates `TMPDIR/files` with mode `1777`, writes `src` and `dst`, and tries to `chown` `dst` to uid 5001. If not root, it attempts to re-exec under `unshare --user --map-root-user --map-users`. It runs `rsync --inplace src dst` and asserts destination content is exactly `"Source\n"`.

State and dependencies: Linux procfs, user namespaces or root, chown permissions, and sticky-directory semantics.

Integration points: receiver open/write behavior for inplace updates under kernel protected-regular restrictions.

Risks and test signals: environment-sensitive with many skip paths. A zero exit is not enough; content verification proves the write occurred.
