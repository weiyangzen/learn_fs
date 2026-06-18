# sources/test-tools/xfstests/tests/f2fs/002

## Purpose

Test that when a file is both compressed and encrypted, the encryption is done correctly. I.e., the correct ciphertext is written to disk. f2fs compression behaves as follows: the original data of a compressed file is divided into equal-sized clusters. The cluster size is configurable, but it must be a power-of-2 multiple of the filesystem block size. If the file size isn't a multiple of the cluster size, then the final cluster is "partial" and holds the remainder modulo the cluster size. Each cluster is compressed independently, encrypted after compression, read back from raw disk blocks, decrypted with fscrypt test tooling, decompressed as LZ4 data, and compared to the original bytes.

## Important APIs, Types, and Functions

This is a bash xfstests case in the `f2fs` suite. The harness entry and tags are `_begin_fstest auto quick rw encrypt compress fiemap`. Important local functions are `decompress_cluster`, `decrypt_blocks`. Key xfstests/helper interfaces include `_require_scratch_f2fs_compression` (requires f2fs compression support), `_require_scratch_encryption` (requires fscrypt support on scratch), `_get_ciphertext_block_list` (derives raw encrypted block locations), `_require_xfs_io_command` (checks xfs_io subcommand support), `_dump_ciphertext_blocks` (reads raw ciphertext blocks from the block device). External or helper commands visible in the body include `awk`, `chattr`, `cmp`, `cp`, `dd`, `fiemap`, `head`, `lz4`, `mkdir`, `od`, and others. Significant variables include `TEST_RAW_KEY_HEX`, `block_size`, `dir`, `file`, `status`.

## Control Flow

The script sources `./common/preamble`, `./common/filter`, `./common/encrypt`, declares prerequisites, prepares test or scratch storage, runs the scenario, verifies results, and exits with `status=0` only after successful checks. Representative operations are: `_require_scratch_encryption -v 2`; `_require_scratch_f2fs_compression lz4`; `_require_command "$CHATTR_PROG" chattr`; `_require_get_encryption_nonce_support`; `_require_xfs_io_command "fiemap" # for _get_ciphertext_block_list()`; `_require_test_program "fscrypt-crypt-util"`; `_require_command "$LZ4_PROG" lz4`.

## State and Persistence Behavior

The test mutates scratch filesystem contents and metadata, mount/unmount state, fscrypt keys, policies, nonces, and ciphertext blocks, compressed extents or clusters. Cleanup is mediated by the xfstests preamble and any registered `_cleanup` function, while remounts, explicit syncs, fsck helpers, and comparison steps are used to prove that user data and filesystem metadata survive the exercised operation.

## Dependencies and Integration Points

Prerequisite gates include `_require_command`, `_require_get_encryption_nonce_support`, `_require_scratch_encryption`, `_require_scratch_f2fs_compression`, `_require_test_program`, `_require_xfs_io_command`. The test integrates with common xfstests libraries through `./common/preamble`, `./common/filter`, `./common/encrypt` and with suite-specific filesystem features selected by the `f2fs` directory, mount options, mkfs options, and helper binaries.

## Risks and Edge Cases

Risks include destructive scratch-device formatting requires correct harness configuration, extent layout assumptions can vary by filesystem feature and kernel version, encryption mode, nonce, and block-size assumptions must match kernel fscrypt behavior, compression heuristics may change block layout while preserving user data. Because this is a filesystem regression test, failures may be caused by kernel bugs, missing userspace helpers, feature-incompatible mkfs/mount options, or environment assumptions rather than shell syntax alone.

## Test Signals

Primary signals: uses byte-for-byte comparison of generated and expected data; logs detailed diagnostics to `$seqres.full`. Skips are expected when `_require_*` gates reject the host, and failures should leave enough detail in `$seqres.full`, normalized stdout, or harness diagnostics to identify the broken operation.
