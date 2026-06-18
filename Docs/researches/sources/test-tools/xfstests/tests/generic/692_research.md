# sources/test-tools/xfstests/tests/generic/692

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/692`. fs-verity requires the filesystem to decide how it stores the Merkle tree, which can be quite large. It is convenient to treat the Merkle tree as past EOF, and ext4, f2fs, and btrfs do so in at least some fashion. This leads to an edge case where a large file can be under the file system file size limit, but trigger EFBIG on enabling fs-verity. Test enabling verity on some large files to exercise EFBIG logic for filesystems with fs-verity specific limits. It is registered with `_begin_fstest auto quick verity`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 83 source line(s).
- Harness registration: `_begin_fstest auto quick verity`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/verity`.
- Capability and skip gates: `_require_test`, `_require_math`, `_require_scratch_verity`, `_require_fsverity_max_file_size_limit`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `fsv_file=$SCRATCH_MNT/file.fsv`
- `max_sz=$(_get_max_file_size $SCRATCH_MNT)`
- `bs=$FSV_BLOCK_SIZE`
- `hash_size=32 # SHA-256`
- `hashes_per_block=$(echo "scale=30; $bs/$hash_size" | $BC -q)`
- `a=$(echo "scale=30; 1/($hashes_per_block^2)" | $BC -q)`
- `r=$(echo "scale=30; 1/$hashes_per_block" | $BC -q)`
- `nonleaves_relative_size=$(echo "scale=30; $a/(1-$r)" | $BC -q)`
- `sz=$(echo "$max_sz/(1+$nonleaves_relative_size)" | $BC -q)`
- `sz=$(echo "$sz - 65536 - $bs*11" | $BC -q)`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_math`, `_require_scratch_verity`, `_require_fsverity_max_file_size_limit`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- Key operational lines include:
- `line 32: _require_scratch_verity`
- `line 36: _scratch_mkfs_verity &>> $seqres.full`
- `line 37: _scratch_mount`
- `line 42: _fsv_scratch_begin_subtest "way too big: fail on first merkle block"`
- `line 44: _fsv_enable $fsv_file |& _filter_scratch`
- `line 77: _fsv_scratch_begin_subtest "still too big: fail on first invalid merkle block"`
- `line 79: _fsv_enable $fsv_file |& _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. fs-verity metadata, signatures, or Merkle trees become durable file metadata and are compared against userspace-computed expectations. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick verity`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/verity`), and the golden-output file `sources/test-tools/xfstests/tests/generic/692.out` (7 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_math`, `_require_scratch_verity`, `_require_fsverity_max_file_size_limit`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.

## Test Signals

The paired `.out` file has 7 line(s); its first visible signals are: "QA output created by 692; # way too big: fail on first merkle block; ERROR: FS_IOC_ENABLE_VERITY failed on 'SCRATCH_MNT/file.fsv': File too large". Runtime pass/fail is also signaled by xfstests output filters, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
