<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/aio.c -->
## sources/test-tools/strace/tests/aio.c

Purpose: Broad decoder test for legacy Linux AIO syscalls: `io_setup`, `io_submit`, `io_getevents`, `io_cancel`, and `io_destroy`.

Important APIs/types/functions: Uses `<linux/aio_abi.h>`, `struct iocb`, `struct io_event`, `kernel_old_timespec_t`, `tail_alloc`, `tail_memdup`, `IOCB_CMD_PREAD/PREADV/PWRITE/PWRITEV`, optional `HAVE_STRUCT_IOCB_AIO_FLAGS`, and raw syscall numbers.

Control flow: Allocates read buffers and IOCB arrays, opens `/dev/zero` on fd 0, probes invalid `io_setup` arguments, creates an AIO context, submits read and vector-read requests, probes invalid pointers/counts, fetches events with invalid and valid timeouts, cancels invalid/constructed requests, submits synthetic IOCBs to cover opcode, priority, buffer, iovec, string, NULL, and bad-pointer decoding, destroys invalid and valid contexts, and exits.

State and persistence: Temporarily owns a kernel AIO context and fd 0 redirected to `/dev/zero`; destroys the context before exit.

Dependencies and integration: Exercises strace AIO structure decoders, iovec/string printers, old timespec decoding, IOCB flag decoding, and architecture-specific integer formatting macros.

Risks: Legacy AIO syscall availability, `/dev/zero`, and kernel limits can skip/fail. Some outputs depend on optional kernel headers and struct fields.

Test signals: Expected output includes successful context setup, decoded IOCB arrays, event result arrays, timeout structures, invalid pointer fallbacks, ioprio formatting, optional `aio_flags/aio_resfd`, and context destruction.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/aio.c -->
