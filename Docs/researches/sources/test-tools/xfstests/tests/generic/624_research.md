# sources/test-tools/xfstests/tests/generic/624

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/624`. Test retrieving the Merkle tree and fs-verity descriptor of a verity file using FS_IOC_READ_VERITY_METADATA. It is registered with `_begin_fstest auto quick verity`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 122 source line(s).
- Harness registration: `_begin_fstest auto quick verity`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/verity`.
- Capability and skip gates: `_require_scratch_verity`, `_require_fsverity_dump_metadata $fsv_file`.
- Local shell functions: `_cleanup`, `test_block_size`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `fsv_orig_file=$SCRATCH_MNT/file`
- `fsv_file=$SCRATCH_MNT/file.fsv`

## Control Flow

- Capability gating runs first through `_require_scratch_verity`, `_require_fsverity_dump_metadata $fsv_file`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 72: echo "Measure returned $actual_file_digest but expected $expected_file_digest"`
- `line 78: echo "Dumped Merkle tree didn't match"`
- `line 86: echo "Dumped Merkle tree (in chunks) didn't match"`
- `line 92: echo "Dumped descriptor didn't match"`
- `line 100: echo "Dumped descriptor (in chunks) didn't match"`
- `line 114: echo "block_size=$block_size is unsupported" >> $seqres.full`
- Key operational lines include:
- `line 24: _require_scratch_verity`
- `line 29: _scratch_mkfs_verity &>> $seqres.full`
- `line 30: _scratch_mount`
- `line 31: _fsv_create_enable_file $fsv_file`
- `line 49: _fsv_enable $fsv_file "${tree_params[@]}"`
- `line 62: local expected_file_digest=$(_fsv_digest $fsv_orig_file \`
- `line 70: local actual_file_digest=$(_fsv_measure $fsv_file)`
- `line 76: _fsv_dump_merkle_tree $fsv_file > $tmp.merkle_tree.actual`
- `line 77: if ! cmp $tmp.merkle_tree.expected $tmp.merkle_tree.actual; then`
- `line 83: _fsv_dump_merkle_tree $fsv_file --offset=$i --length=997`
- `line 85: if ! cmp $tmp.merkle_tree.expected $tmp.merkle_tree.actual; then`
- `line 90: _fsv_dump_descriptor $fsv_file > $tmp.descriptor.actual`
- `line 91: if ! cmp $tmp.descriptor.expected $tmp.descriptor.actual; then`
- `line 97: _fsv_dump_descriptor $fsv_file --offset=$i --length=13`
- `line 99: if ! cmp $tmp.descriptor.expected $tmp.descriptor.actual; then`
- `line 106: _fsv_scratch_begin_subtest "Testing block_size=FSV_BLOCK_SIZE"`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. fs-verity metadata, signatures, or Merkle trees become durable file metadata and are compared against userspace-computed expectations. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick verity`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/verity`), and the golden-output file `sources/test-tools/xfstests/tests/generic/624.out` (11 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_verity`, `_require_fsverity_dump_metadata $fsv_file`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 11 line(s); its first visible signals are: 'QA output created by 624; # Testing block_size=FSV_BLOCK_SIZE; # Testing block_size=1024 if supported'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
