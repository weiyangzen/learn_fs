## sources/test-tools/xfstests/tests/btrfs/001

Purpose: this quick btrfs test exercises basic subvolume and snapshot behavior, default subvolume selection, and subvolume deletion.

Control flow: after `_begin_fstest auto quick subvol snapshot`, it sources generic and btrfs filters, requires scratch, reformats and mounts it, creates `foo`, snapshots the root to `snap`, verifies root and snapshot directory listings diverge after removing `foo`, creates `subvol`, writes `bar`, sets `subvol` as the default using `_btrfs_get_subvolid`, remounts to verify the default view, mounts `subvolid=0` to restore root access, resets the default to root, lists subvolumes, deletes `snap`, and checks listings across a remount.

Important dependencies: `common/preamble`, `common/filter`, `common/filter.btrfs`, `_scratch_mkfs`, `_scratch_mount`, `_scratch_cycle_mount`, `_scratch_unmount`, `$BTRFS_UTIL_PROG`, `_btrfs`, `_btrfs_get_subvolid`, `_filter_scratch`, and `_filter_btrfs_subvol_delete`.

State and persistence: all state is on the scratch filesystem: `foo`, `snap`, `subvol`, default-subvolume metadata, and the file `bar`. The test resets the default subvolume to root before exit.

Risks: directory listing order can affect output if filesystem/tool behavior changes. A failed reset of the default subvolume can leave scratch in a confusing state until reformatted. The text contains a harmless typo in the printed "sbuvolid".

Test signals: expected stdout describes each operation and stable `ls` output. Failures are command errors from btrfs subvolume operations, mount failures after changing the default, or mismatched golden output.
