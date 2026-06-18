# sources/test-tools/xfstests/tests/generic/739

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/739`. Verify the on-disk format of encrypted files that use a crypto data unit size that differs from the filesystem block size. This tests the functionality that was introduced in Linux 6.7 by kernel commit 5b1188847180 ("fscrypt: support crypto data unit size less than filesystem block size"). It is registered with `_begin_fstest auto quick encrypt`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 30 source line(s).
- Harness registration: `_begin_fstest auto quick encrypt`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/encrypt`.
- Capability and skip gates: `_wants_kernel_commit 5b1188847180 "fscrypt: support crypto data unit size less than filesystem block size"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_wants_kernel_commit 5b1188847180 "fscrypt: support crypto data unit size less than filesystem block size"`.
- Key operational lines include:
- `line 25: _verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-CTS-CBC v2 log2_dusize=9`
- `line 26: _verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-CTS-CBC v2 log2_dusize=10`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Encryption policy/key state is created during the test and used to check no-key/key-present transitions. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick encrypt`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/encrypt`), and the golden-output file `sources/test-tools/xfstests/tests/generic/739.out` (11 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_wants_kernel_commit 5b1188847180 "fscrypt: support crypto data unit size less than filesystem block size"`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 11 line(s); its first visible signals are: 'QA output created by 739; Verifying ciphertext with parameters:; contents_encryption_mode: AES-256-XTS; filenames_encryption_mode: AES-256-CTS-CBC'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
