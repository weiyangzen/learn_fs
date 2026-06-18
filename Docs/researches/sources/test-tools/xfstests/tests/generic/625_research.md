# sources/test-tools/xfstests/tests/generic/625

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/625`. Test retrieving the built-in signature of a verity file using FS_IOC_READ_VERITY_METADATA. This is separate from the other tests for FS_IOC_READ_VERITY_METADATA because the fs-verity built-in signature support is optional. It is registered with `_begin_fstest auto quick verity`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 50 source line(s).
- Harness registration: `_begin_fstest auto quick verity`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/verity`.
- Capability and skip gates: `_require_scratch_verity`, `_require_fsverity_builtin_signatures`, `_require_fsverity_dump_metadata $fsv_file`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `fsv_file=$SCRATCH_MNT/file`
- `sig_size=$(stat -c %s $tmp.sig)`

## Control Flow

- Capability gating runs first through `_require_scratch_verity`, `_require_fsverity_builtin_signatures`, `_require_fsverity_dump_metadata $fsv_file`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 25: echo -e "\n# Setting up signed verity file"`
- `line 30: echo foo > $fsv_file`
- `line 35: echo -e "\n# Dumping and comparing signature"`
- `line 41: echo -e "\n# Dumping and comparing signature (in chunks)"`
- Key operational lines include:
- `line 19: _require_scratch_verity`
- `line 22: _scratch_mkfs_verity &>> $seqres.full`
- `line 23: _scratch_mount`
- `line 26: _fsv_generate_cert $tmp.key $tmp.cert $tmp.cert.der`
- `line 27: _fsv_clear_keyring`
- `line 28: _fsv_load_cert $tmp.cert.der`
- `line 31: _fsv_sign $fsv_file $tmp.sig --key=$tmp.key --cert=$tmp.cert >> $seqres.full`
- `line 32: _fsv_enable $fsv_file --signature=$tmp.sig`
- `line 36: _fsv_dump_signature $fsv_file > $tmp.sig2`
- `line 39: cmp $tmp.sig $tmp.sig2`
- `line 42: sig_size=$(stat -c %s $tmp.sig)`
- `line 44: _fsv_dump_signature $fsv_file --offset=$i --length=13`
- `line 46: cmp $tmp.sig $tmp.sig2`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. fs-verity metadata, signatures, or Merkle trees become durable file metadata and are compared against userspace-computed expectations. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick verity`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/verity`), and the golden-output file `sources/test-tools/xfstests/tests/generic/625.out` (7 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_verity`, `_require_fsverity_builtin_signatures`, `_require_fsverity_dump_metadata $fsv_file`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 7 line(s); its first visible signals are: 'QA output created by 625; # Setting up signed verity file; # Dumping and comparing signature'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
