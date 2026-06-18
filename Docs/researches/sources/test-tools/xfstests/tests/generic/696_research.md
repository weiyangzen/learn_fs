# sources/test-tools/xfstests/tests/generic/696

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/696`. Test S_ISGID stripping whether works correctly when call process uses umask(S_IXGRP). It is also a regression test for commit ac6800e279a2 ("fs: Add missing umask strip in vfs_tmpfile") commit 1639a49ccdce ("fs: move S_ISGID stripping into the vfs_*() helpers") It is registered with `_begin_fstest auto quick cap idmapped mount perms rw unlink`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 47 source line(s).
- Harness registration: `_begin_fstest auto quick cap idmapped mount perms rw unlink`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_scratch`, `_require_chmod`, `_fixed_by_kernel_commit ac6800e279a2 "fs: Add missing umask strip in vfs_tmpfile" 1639a49ccdce "fs: move S_ISGID stripping into the vfs_*() helpers"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-setgid-create-umask \`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_scratch`, `_require_chmod`, `_fixed_by_kernel_commit ac6800e279a2 "fs: Add missing umask strip in vfs_tmpfile" 1639a49ccdce "fs: move S_ISGID stripping into the vfs_*() helpers"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 45: echo "Silence is golden"`
- Key operational lines include:
- `line 27: _scratch_mkfs >$seqres.full 2>&1`
- `line 41: _try_scratch_mount >>$seqres.full 2>&1 && \`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick cap idmapped mount perms rw unlink`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/696.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_scratch`, `_require_chmod`, `_fixed_by_kernel_commit ac6800e279a2 "fs: Add missing umask strip in vfs_tmpfile" 1639a49ccdce "fs: move S_ISGID stripping into the vfs_*() helpers"`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 696; Silence is golden'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
