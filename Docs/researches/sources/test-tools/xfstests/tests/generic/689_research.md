# sources/test-tools/xfstests/tests/generic/689

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/689`. Test that setting POSIX ACLs in userns-mountable filesystems works. Regression test for commit: 705191b03d50 ("fs: fix acl translation") It is registered with `_begin_fstest auto quick perms idmapped`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 33 source line(s).
- Harness registration: `_begin_fstest auto quick perms idmapped`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/attr`.
- Capability and skip gates: `_require_test`, `_require_idmapped_mounts`, `_require_acls`, `_require_user fsgqa`, `_require_group fsgqa`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/vfs/vfstest --test-setxattr-fix-705191b03d50 \`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_idmapped_mounts`, `_require_acls`, `_require_user fsgqa`, `_require_group fsgqa`.
- User-visible phase markers include:
- `line 27: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick perms idmapped`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/attr`), and the golden-output file `sources/test-tools/xfstests/tests/generic/689.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_idmapped_mounts`, `_require_acls`, `_require_user fsgqa`, `_require_group fsgqa`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 689; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
