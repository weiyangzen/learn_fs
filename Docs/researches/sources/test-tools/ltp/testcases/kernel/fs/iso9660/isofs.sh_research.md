# sources/test-tools/ltp/testcases/kernel/fs/iso9660/isofs.sh

## Purpose

`isofs.sh` tests ISO9660 image creation and mounting with different mkisofs-compatible tools, image options, and kernel mount options.

## Important APIs, Types, and Functions

It uses modern LTP shell variables `TST_NEEDS_CMDS`, `TST_NEEDS_TMPDIR`, `TST_NEEDS_KCONFIGS`, `TST_TESTFUNC`, `TST_CNT`, and `TST_SETUP`. Functions are `setup`, `gen_fs_tree`, and `do_test`.

## Control Flow

`setup` discovers the group for user `nobody`. For each of three test counts, `do_test` selects `mkisofs`, `genisoimage`, or `xorrisofs`, confirms the command exists and is not a symlink to another tool, creates a nested random file tree, creates `isofs.iso` with several option sets, then mounts and unmounts it with many ISO9660 mount options.

## State and Persistence Behavior

All files live under the LTP tmpdir: `files/`, `mnt/`, and `isofs.iso`. `gen_fs_tree` creates a depth-limited tree with random 100 KiB files.

## Dependencies and Integration Points

Requires kernel `CONFIG_ISO9660_FS`, `mount`, `umount`, one of the mkisofs-compatible tools per subtest, loop mounts, and the modern `tst_test.sh` shell API.

## Risks and Edge Cases

The test dynamically handles missing image tools as `TCONF`, but `TST_NEEDS_CMDS` does not predeclare them. Some mount options may be unsupported on newer kernels or by malformed images and are handled through `EXPECT_PASS`/`continue`. Random input data makes exact images non-reproducible.

## Test Signals

Each successful mount/list/unmount combination emits `TPASS`. Missing image tools or symlinked aliases produce `TCONF`; mount, image creation, or unmount failures are reported through `EXPECT_PASS` helpers.
