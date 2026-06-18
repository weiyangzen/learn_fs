# sources/test-tools/xfstests/tests/generic/656

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/656`. This is a test for the fix commit 968219708108 ("fs: handle circular mappings correctly") in Linux. It verifies that setattr for {g,u}id work correctly. It is registered with `_begin_fstest auto attr cap idmapped mount perms`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 32 source line(s).
- Harness registration: `_begin_fstest auto attr cap idmapped mount perms`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_idmapped_mounts`, `_require_test`, `_require_chown`, `_require_user fsgqa`, `_require_user fsgqa2`, `_require_group fsgqa`, `_require_group fsgqa2`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-setattr-fix-968219708108 \`.

## Control Flow

- Capability gating runs first through `_require_idmapped_mounts`, `_require_test`, `_require_chown`, `_require_user fsgqa`, `_require_user fsgqa2`, plus 2 more.
- User-visible phase markers include:
- `line 26: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Extended attributes are part of the persistent state being created, replayed, or verified. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto attr cap idmapped mount perms`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/656.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_idmapped_mounts`, `_require_test`, `_require_chown`, `_require_user fsgqa`, `_require_user fsgqa2`, `_require_group fsgqa`, `_require_group fsgqa2`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 656; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
