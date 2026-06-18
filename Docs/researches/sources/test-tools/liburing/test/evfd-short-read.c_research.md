<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/evfd-short-read.c -->
## sources/test-tools/liburing/test/evfd-short-read.c

Purpose: regression test for eventfd short-read handling when a read buffer is larger than one eventfd counter value.

Important APIs/types/functions: `eventfd(EFD_NONBLOCK)`, `io_uring_prep_read`, `io_uring_wait_cqe`, `sigaction`, `alarm`, and the timeout handler `sig_alrm`.

Control flow: the test submits a read for two `uint64_t` eventfd values, waits briefly, writes one eventfd value, then waits for the CQE. A one-second alarm fails the test if the kernel incorrectly waits for the full larger buffer.

State and persistence behavior: eventfd state is a single counter increment. The ring has one pending read and the eventfd is closed after completion.

Dependencies and integration points: relies on anonymous-inode eventfd semantics and io_uring read retry/short-read logic.

Risks: the test does not inspect `cqe->res`, so its primary signal is absence of hang rather than exact returned byte count. Timing is guarded by `alarm`.

Test signals: pass indicates io_uring completes a partial eventfd read once one event is available instead of treating eventfd like a regular file requiring the full buffer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/evfd-short-read.c -->
