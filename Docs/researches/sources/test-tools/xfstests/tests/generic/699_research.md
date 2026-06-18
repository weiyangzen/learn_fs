# sources/test-tools/xfstests/tests/generic/699

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/699`. This's copied from generic/698, extend it to test overlayfs on top of idmapped mounts specifically. It is registered with `_begin_fstest auto quick perms attr idmapped mount`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 166 source line(s).
- Harness registration: `_begin_fstest auto quick perms attr idmapped mount`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_exclude_fs overlay`, `_require_extra_fs overlay`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, `_require_test_program "vfs/mount-idmapped"`, `_require_user fsgqa2`, `_require_group fsgqa2`, `_require_user fsgqa`, `_require_group fsgqa`, plus 1 more.
- Local shell functions: `_cleanup`, `setup_tree`, `setup_idmapped_mnt`, `change_group_ownership`, `reset_ownership`, `setup_overlayfs`, `setup_overlayfs_idmapped_lower_metacopy_off`, `setup_overlayfs_idmapped_lower_metacopy_on`, `reset_overlayfs`, `run_overlayfs_idmapped_lower_metacopy_off`, `run_overlayfs_idmapped_lower_metacopy_on`.
- External `$here/src` helpers: `$here/src/vfs/mount-idmapped \`.
- Notable variables and constants:
- `user_foo=`id -u fsgqa``
- `group_foo=`id -g fsgqa``
- `user_bar=`id -u fsgqa2``
- `group_bar=`id -g fsgqa2``
- `lower="$SCRATCH_MNT/target-mnt"`
- `upper="$SCRATCH_MNT/ovl-upper"`
- `work="$SCRATCH_MNT/ovl-work"`
- `merge="$SCRATCH_MNT/ovl-merge"`

## Control Flow

- Capability gating runs first through `_exclude_fs overlay`, `_require_extra_fs overlay`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, plus 6 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 90: echo ""`
- `line 91: echo "reset ownership"`
- `line 131: echo ""`
- `line 132: echo "overlayfs idmapped lower metacopy off"`
- `line 145: echo ""`
- `line 146: echo "overlayfs idmapped lower metacopy on"`
- Key operational lines include:
- `line 17: _unmount $SCRATCH_MNT/target-mnt`
- `line 18: _unmount $SCRATCH_MNT/ovl-merge 2>/dev/null`
- `line 19: _unmount $SCRATCH_MNT 2>/dev/null`
- `line 29: _require_test_program "vfs/mount-idmapped"`
- `line 58: $here/src/vfs/mount-idmapped \`
- `line 74: stat -c '%U:%G' $path`
- `line 76: stat -c '%U:%G' $path`
- `line 78: stat -c '%U:%G' $path`
- `line 93: stat -c '%u:%g' $path`
- `line 95: stat -c '%u:%g' $path`
- `line 101: _mount -t overlay -o lowerdir=$lower,upperdir=$upper,workdir=$work \`
- `line 120: _unmount $SCRATCH_MNT/ovl-merge 2>/dev/null`
- `line 152: _scratch_mkfs >> $seqres.full`
- `line 153: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick perms attr idmapped mount`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/699.out` (27 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_exclude_fs overlay`, `_require_extra_fs overlay`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, `_require_test_program "vfs/mount-idmapped"`, `_require_user fsgqa2`, `_require_group fsgqa2`, plus 3 more.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 27 line(s); its first visible signals are: 'QA output created by 699; overlayfs idmapped lower metacopy off; fsgqa:fsgqa2; fsgqa'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
