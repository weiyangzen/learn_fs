# File Research: sources/local-fs/gfs2-utils/tests/fsck.gfs2-tester.sh

Shell test runner for replaying metadata images through `gfs2_edit restoremeta` and `fsck.gfs2`.

Usage:
- `fsck.gfs2-tester.sh <path> <truncate_size>`
- Reads stdin lines of `<clean|dirty> <path>` metadata cases.

Behavior:
- Validates/touches target device/file.
- Creates timestamped result directory.
- For each case, restores metadata to target.
- For `clean`, runs `fsck.gfs2 -n` and expects success.
- For `dirty`, runs `fsck.gfs2 -y` and expects return code `1`, then `fsck.gfs2 -n` and expects success.
- Removes per-case logs for passing tests.
- Writes failed cases to `fsck.gfs2.fails.in`.

Research notes:
- Designed to destroy target contents.
- Sparse file mode is supported through nonzero `truncate_size`.
