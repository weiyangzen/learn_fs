# sources/test-tools/strace/src/aio.c

Purpose: decoders for Linux native AIO syscalls: `io_setup`, `io_destroy`, `io_submit`, `io_cancel`, `io_getevents`, and `io_pgetevents` time variants.

Important APIs/types/functions: `tprint_lio_opcode`, `print_common_flags`, `iocb_is_valid`, `print_iocb_header`, `print_iocb`, `print_iocbp`, `print_io_event`, `print_io_getevents`, xlat `aio_cmds`, optional `aio_iocb_flags`, `rwf_flags`, `pollflags`, and time/sigset printers.

Control flow: setup/destroy print context identifiers and output pointers. `io_submit` prints an array of iocb pointers and each pointed-to iocb with opcode-specific body handling for common buffer ops, vector ops, poll, or no-extra-data commands. `io_cancel` prints the iocb header on entry and result event on exit. `io_getevents` prints scalar inputs on entry and event array plus timeout/sigset on exit, temporarily clearing syscall error so entry-read timeout/sig args are decoded even on failure.

State and persistence behavior: no persistent decoder state. It reads tracee memory for iocb pointers, iocb structures, event arrays, iovecs, strings, timespecs, and sigsets.

Dependencies and integration points: relies on `<linux/aio_abi.h>` field availability configure checks, generic array printers, mpers-neutral kernel integer truncation, and architecture time32/time64 feature macros.

Risks: opcode checks use numeric values in a few spots (`aio_lio_opcode == 1`, vector opcode `8`) alongside constants, which can be brittle. Invalid user pointers or mismatched structure sizes fall back to addresses. Conditional fields must match configured kernel headers.

Test signals: AIO decoder tests should cover read/write/vector/poll iocbs, `IOCB_FLAG_RESFD`, `IOCB_FLAG_IOPRIO`, cancellation result, event arrays, time32/time64 paths, and failed calls.
