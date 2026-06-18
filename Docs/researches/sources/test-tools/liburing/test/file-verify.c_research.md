<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/file-verify.c -->
## sources/test-tools/liburing/test/file-verify.c

Purpose: large data-integrity test for buffered and direct reads across vectored, fixed-buffer, provided-buffer, and truncation/short-read cases.

Important APIs/types/functions: `verify_buf`, `test_truncate`, `do_punch`, `provide_buffers`, `test`, `fill_pattern`, `io_uring_prep_read`, `io_uring_prep_readv`, `io_uring_prep_read_fixed`, `io_uring_prep_provide_buffers`, `IOSQE_BUFFER_SELECT`, and `t_register_buffers`.

Control flow: `main` creates or uses a 128 MiB file, fills it with offset-derived integer patterns, then runs buffered and O_DIRECT read passes with plain buffers, registered buffers, provided buffers, large/small iovec arrays, and truncation-like short reads near file end. Each read batch validates returned bytes against expected file offsets.

State and persistence behavior: the test file is filled with deterministic content. `posix_fadvise(... DONTNEED)` creates cache holes to force incremental buffered read paths. Registered buffers are unregistered after each pass.

Dependencies and integration points: touches page cache behavior, O_DIRECT alignment, provided buffers, registered buffers, block-device size queries, and architecture-specific hppa cache flush handling.

Risks: high IO volume and filesystem/direct-IO support requirements. The test skips unsupported direct IO and permission cases.

Test signals: pass is a strong end-to-end data integrity signal for read result length, buffer selection, and retry behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/file-verify.c -->
