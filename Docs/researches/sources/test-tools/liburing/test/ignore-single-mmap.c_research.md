<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/ignore-single-mmap.c -->
## sources/test-tools/liburing/test/ignore-single-mmap.c

Purpose: regression test for applications that ignore `IORING_FEAT_SINGLE_MMAP` and still perform smaller legacy-style ring mmaps.

Important APIs/types/functions: raw `__sys_io_uring_setup`, raw `__sys_mmap`, `IORING_OFF_SQ_RING`, `IORING_FEAT_SINGLE_MMAP`, `IS_ERR`, and `PTR_ERR`.

Control flow: the test sets up a ring with 128 entries through the raw syscall, skips if setup fails or single-mmap feature is absent, then mmaps only the SQ ring-sized area at `IORING_OFF_SQ_RING`. Success passes; mmap error fails.

State and persistence behavior: one raw ring fd is created and closed only on the pass/skip paths before failure. The mapping is not explicitly unmapped.

Dependencies and integration points: targets kernel mmap ABI compatibility for io_uring ring layout.

Risks: low-level syscall use bypasses liburing cleanup. Failure catches kernels returning `-EFAULT` for valid smaller mappings.

Test signals: pass means single-mmap rings still tolerate legacy segmented mmap calls.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/ignore-single-mmap.c -->
