# File Research: sources/virtualization/qemu/block/blkverify.c

This file implements the `blkverify` block protocol/filter for comparing a test image against a raw reference image.

State and open:
- `BDRVBlkverifyState` stores a `test_file` child; the raw/reference child is the standard `bs->file`.
- `blkverify_parse_filename()` accepts `blkverify:raw:image` and maps paths into internal `x-raw` and `x-image`.
- `blkverify_open()` opens the raw file child and the test child, then advertises `BDRV_REQ_WRITE_UNCHANGED` for write and zero flags.

Verification flow:
- `blkverify_co_prwv()` creates two coroutines: one I/O to the test child and one to the raw child.
- It waits until both complete, compares return codes, and aborts the entire QEMU process on mismatch via `blkverify_err()`.
- `blkverify_co_preadv()` allocates an aligned buffer for the raw read, clones the caller I/O vector, performs both reads, then compares returned data using `qemu_iovec_compare()`.
- `blkverify_co_pwritev()` writes the same buffer to both images.
- Flush only flushes the test file because the raw file is considered nonessential for flush verification.

Graph behavior:
- `blkverify_recurse_can_replace()` allows replacement recursion through either child because mismatch-free operation implies equivalence.
- `blkverify_refresh_filename()` synthesizes `blkverify:raw:test` only when both children have exact filenames.
- `blkverify_dirname()` always fails because two children may have different base directories.

Filesystem/block relevance:
- This is a correctness-testing filter for image drivers.
- It is useful when validating that a format driver returns the same data and error behavior as a raw reference.

Potential pitfalls:
- Any mismatch calls `exit(1)`, so this is a test/debug tool rather than production infrastructure.
- Read comparison clears `BDRV_REQ_REGISTERED_BUF` for the raw side because the cloned buffer is not necessarily registered.
- It does not implement discard/write-zeroes verification wrappers in this file, only read/write/flush.
