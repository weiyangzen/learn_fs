<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-seg.c -->
## sources/test-tools/liburing/test/fixed-seg.c

Purpose: tests fixed-buffer segment validation for O_DIRECT reads, including offsets inside a registered buffer.

Important APIs/types/functions: `read_it`, `test`, `is_bdev`, `io_uring_register_buffers`, `io_uring_prep_read_fixed`, `BLKGETSIZE64`, and aligned iovecs.

Control flow: the test opens a supplied file/block device or creates a temporary direct-IO file, registers read/write buffers, and issues fixed reads with varying lengths and offsets into the registered segment. It uses block-device detection to decide whether a supplied fd is acceptable.

State and persistence behavior: global `rvec` and `wvec` hold aligned registered buffers. Temporary files are unlinked when created by the test.

Dependencies and integration points: depends on O_DIRECT compatibility, block-device or regular-file sizing, and fixed buffer offset accounting.

Risks: direct IO support and alignment rules are environment-sensitive. Bad segment validation can surface as short reads or negative CQE results.

Test signals: pass means fixed-buffer segments and offsets are accepted only when valid and complete with expected lengths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-seg.c -->
