# sources/test-tools/xfstests/tests/generic/698

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/698`. Test that users can changed group ownership of a file they own to a group they are a member of. Regression test for commit: 168f91289340 ("fs: account for group membership") It is registered with `_begin_fstest auto quick perms attr idmapped mount`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 115 source line(s).
- Harness registration: `_begin_fstest auto quick perms attr idmapped mount`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_kernel_commit 168f91289340 "fs: account for group membership"`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, `_require_test_program "vfs/mount-idmapped"`, `_require_user fsgqa2`, `_require_group fsgqa2`, `_require_user fsgqa`, `_require_group fsgqa`.
- Local shell functions: `_cleanup`, `setup_tree`, `setup_idmapped_mnt`, `change_group_ownership`, `run_base_test`, `run_idmapped_test`.
- External `$here/src` helpers: `$here/src/vfs/mount-idmapped \`.
- Notable variables and constants:
- `user_foo=`id -u fsgqa``
- `group_foo=`id -g fsgqa``
- `user_bar=`id -u fsgqa2``
- `group_bar=`id -g fsgqa2``

## Control Flow

- Capability gating runs first through `_fixed_by_kernel_commit 168f91289340 "fs: account for group membership"`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, `_require_test_program "vfs/mount-idmapped"`, plus 4 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 91: echo ""`
- `line 92: echo "base test"`
- `line 100: echo ""`
- `line 101: echo "base idmapped test"`
- Key operational lines include:
- `line 20: _unmount $SCRATCH_MNT/target-mnt 2>/dev/null`
- `line 21: _unmount $SCRATCH_MNT 2>/dev/null`
- `line 30: _require_test_program "vfs/mount-idmapped"`
- `line 59: $here/src/vfs/mount-idmapped \`
- `line 75: stat -c '%U:%G' $path`
- `line 77: stat -c '%U:%G' $path`
- `line 79: stat -c '%U:%G' $path`
- `line 105: _scratch_mkfs >> $seqres.full`
- `line 106: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick perms attr idmapped mount`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/698.out` (19 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_kernel_commit 168f91289340 "fs: account for group membership"`, `_require_scratch`, `_require_chown`, `_require_idmapped_mounts`, `_require_test_program "vfs/mount-idmapped"`, `_require_user fsgqa2`, `_require_group fsgqa2`, `_require_user fsgqa`, plus 1 more.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 19 line(s); its first visible signals are: 'QA output created by 698; base test; fsgqa:fsgqa2; fsgqa'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
