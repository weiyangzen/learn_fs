# sources/test-tools/xfstests/tests/generic/693

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/693`. Verify ciphertext for v2 encryption policies that use AES-256-XTS to encrypt file contents and AES-256-HCTR2 to encrypt file names. HCTR2 was introduced in kernel commit 6b2a51ff03bf ("fscrypt: Add HCTR2 support for filename encryption") It is registered with `_begin_fstest auto quick encrypt`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 29 source line(s).
- Harness registration: `_begin_fstest auto quick encrypt`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/encrypt`.
- Capability and skip gates: none visible.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- After harness setup, the script executes its helper or shell reproducer and lets the xfstests runner compare output and exit status.
- Key operational lines include:
- `line 21: _verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-HCTR2 v2`
- `line 22: _verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-HCTR2 \`
- `line 24: _verify_ciphertext_for_encryption_policy AES-256-XTS AES-256-HCTR2 \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Encryption policy/key state is created during the test and used to check no-key/key-present transitions. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick encrypt`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/encrypt`), and the golden-output file `sources/test-tools/xfstests/tests/generic/693.out` (16 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: none visible.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 16 line(s); its first visible signals are: 'QA output created by 693; Verifying ciphertext with parameters:; contents_encryption_mode: AES-256-XTS; filenames_encryption_mode: AES-256-HCTR2'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
