# sources/test-tools/xfstests/tests/btrfs/214

## Purpose

`sources/test-tools/xfstests/tests/btrfs/214` is btrfs fstests case `214`. It targets subvolume/snapshot metadata, send/receive stream correctness. Source comments describe the scenario as: Test if the file capabilities aren't lost after full and incremental send Test full send containing a file without capabilities ensure that we don't have capabilities set Test if incremental send brings the newly added capability files should include foo.bar create files on fs1, must contain foo.bar Test full send, checking if the receiving side keeps the capabilities Test incremental send with different owner/group but same capabilities Test capabilities after incremental send with different group and capabilities

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send snapshot` declares tags `auto quick send snapshot`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_command "$SETCAP_PROG" setcap`, `_require_command "$GETCAP_PROG" getcap`; local shell helpers: `cleanup()`, `check_capabilities()`, `setup()`, `full_nocap_inc_withcap_send()`, `roundtrip_send()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_command "$SETCAP_PROG" setcap`; `_require_command "$GETCAP_PROG" getcap`; `FS1="$SCRATCH_MNT/fs1"`; `FS2="$SCRATCH_MNT/fs2"`; `ret=$(_getcap "$file")`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create "$FS1" > /dev/null`; `$BTRFS_UTIL_PROG subvolume create "$FS2" > /dev/null`; `full_nocap_inc_withcap_send()`; `$BTRFS_UTIL_PROG subvolume snapshot -r "$FS1" "$FS1/snap_init" >/dev/null`; `full_nocap_inc_withcap_send`; `roundtrip_send "foo.bar"`; `roundtrip_send "foo.bar foo.bax foo.baz"`; `roundtrip_send "foo1 foo.bar foo3"`; `roundtrip_send "foo1 foo2 foo.bar"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send snapshot` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Linux file capability xattrs must survive the send/receive sequence.
