# sources/test-tools/ltp/testcases/kernel/syscalls/fallocate/fallocate03.c

Purpose: Tests successful `fallocate()` on a sparse file at several offsets, both default and keep-size.

Important APIs/types/functions: `SAFE_OPEN`, `SAFE_FSTAT`, `SAFE_WRITE`, `SAFE_LSEEK`, `fallocate`, `FALLOC_FL_KEEP_SIZE`, and table-driven offsets in filesystem block units.

Control flow: `setup()` writes 12 blocks, seeks across a 12-block hole, writes 12 more blocks, and rewinds. Each row fallocates one block at an offset inside data, hole, or beyond-hole regions.

State and persistence behavior: State is a sparse temp file with data-hole-data layout. The test validates allocation succeeds in each region.

Dependencies and integration points: Runs in a tmpdir with modern LTP macros.

Risks and test signals: It does not verify resulting extents or contents, only syscall success. Unsupported sparse/allocation semantics would surface as failed `fallocate`.
