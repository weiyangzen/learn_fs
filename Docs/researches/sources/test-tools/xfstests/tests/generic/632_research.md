# sources/test-tools/xfstests/tests/generic/632

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/632`. Regression test to verify that creating a series of detached mounts, attaching them to the filesystem, and unmounting them does not trigger an integer overflow in ns->mounts causing the kernel to block any new mounts in count_mounts() and returning ENOSPC because it falsely assumes that the maximum number of mounts in the mount namespace has been reached, i.e. it thinks it can't fit the new mounts into the mount namespace anymore. Kernel commit ee2e3f50629f ("mount: fix mounting of detached mounts onto targets that reside on shared mounts") fixed the bug. It is registered with `_begin_fstest auto quick mount`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 31 source line(s).
- Harness registration: `_begin_fstest auto quick mount`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_test`, `_require_test_program "detached_mounts_propagation"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/detached_mounts_propagation $TEST_DIR >> $seqres.full`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_test_program "detached_mounts_propagation"`.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 30: echo silence is golden`
- Key operational lines include:
- `line 25: _mount --make-shared $TEST_DIR`
- `line 28: _mount --make-private $TEST_DIR`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick mount`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/632.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_test_program "detached_mounts_propagation"`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 632; silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
