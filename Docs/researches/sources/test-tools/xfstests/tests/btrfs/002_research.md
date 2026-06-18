## sources/test-tools/xfstests/tests/btrfs/002

Purpose: this extended snapshot test verifies that modifying snapshots through allocation, append, read-modify-write, nested snapshots, and source deletion does not corrupt the original subvolume contents.

Important local APIs: `_save_checksum fs sumfile` records SHA256 checksums for all files under a tree. `_verify_checksum fs sumfile` runs `sha256sum -c` and prints failures. `_create_snap dest` creates a uniquely named snapshot under scratch and stores it in `SNAPNAME`. `_read_modify_write`, `_fill_blk`, and `_append_file` apply different write patterns to files in a target tree.

Control flow: it creates subvolume `sv1`, populates a deep compressible tree with `_populate_fs`, snapshots it, records checksums, modifies only the snapshot through block filling, appending, and read-modify-write, and repeatedly verifies the original. It then creates seven nested snapshots and verifies each against the original checksum. Finally it snapshots again, records the snapshot checksum, deletes all original files, and verifies the snapshot still matches.

State and persistence: scratch contains `sv1`, multiple `snap.*` snapshots, temporary checksum files under `$tmp`, and populated file trees. The test unmounts scratch at the end.

Dependencies: `common/preamble`, `common/filter`, `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, `_populate_fs`, `$BTRFS_UTIL_PROG`, `_ddt`, `dd`, `sha256sum`, `find`, and `stat`.

Risks: unquoted `find` results and checksum paths are unsafe for filenames with whitespace, though `_populate_fs` generates simple names. Background `dd` jobs use `wait $!`, which only waits for the last background job in some helpers; this is adequate for the generated workload but fragile as a pattern.

Test signals: the test prints `Silence is golden`; any `FAILED` checksum line or explicit `_fail` is a regression signal.
