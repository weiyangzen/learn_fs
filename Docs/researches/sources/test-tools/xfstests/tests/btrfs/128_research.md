# sources/test-tools/xfstests/tests/btrfs/128

## Purpose

`sources/test-tools/xfstests/tests/btrfs/128` is btrfs fstests case `128`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that, under a particular scenario, an incremental send operation does not leak memory (which used to emit a warning in dmesg/syslog). Filesystem looks like: .                                                             (ino 256) |--- a/                                                       (ino 257) |    |--- c/                                                  (ino 260) |--- del/                                                     (ino 259) |--- tmp/                                               (ino 258) |--- x/                                                 (ino 261) |--- y/                                                 (ino 262)

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap2`; `run_check $FSSUM_PROG -A -f -w $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `run_check $FSSUM_PROG -A -f -w $send_files_dir/2.fssum \`; `_scratch_unmount`; `_btrfs receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `run_check $FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `_btrfs receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `run_check $FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. `fssum` manifests are written on source snapshots and verified after receive.
