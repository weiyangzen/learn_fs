# sources/test-tools/xfstests/tests/generic/644

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/644`. Test that fscaps on idmapped mounts behave correctly. It is registered with `_begin_fstest auto quick cap idmapped mount`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 25 source line(s).
- Harness registration: `_begin_fstest auto quick cap idmapped mount`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_idmapped_mounts`, `_require_test`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-fscaps-regression \`.

## Control Flow

- Capability gating runs first through `_require_idmapped_mounts`, `_require_test`.
- User-visible phase markers include:
- `line 19: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick cap idmapped mount`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/644.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_idmapped_mounts`, `_require_test`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 644; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
