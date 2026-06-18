<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fadvise.c -->
## sources/test-tools/liburing/test/fadvise.c

Purpose: basic `IORING_OP_FADVISE` coverage with cache-drop and prefetch advisory patterns.

Important APIs/types/functions: `do_fadvise`, `do_read`, `test_fadvise`, `io_uring_prep_fadvise`, `POSIX_FADV_DONTNEED`, `POSIX_FADV_WILLNEED`, `utime_since_now`, and `t_create_file`.

Control flow: the test opens a supplied or temporary file, measures an initial cached read, submits DONTNEED, reads again, submits DONTNEED then WILLNEED, and reads a third time. It repeats up to 100 loops but exits after at least ten good timing iterations with no bad samples.

State and persistence behavior: temporary `.fadvise.tmp` is created when no path is supplied and removed on exit. The ring has one fadvise SQE per advisory call.

Dependencies and integration points: depends on filesystem advisory behavior and liburing's fadvise prep wrapper.

Risks: timing comparisons are explicitly disabled as hard failure because cache behavior is noisy. Unsupported fadvise returns `-EINVAL` or `-EBADF` and skips.

Test signals: strong signal is successful fadvise CQEs; timing is informational only.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fadvise.c -->
