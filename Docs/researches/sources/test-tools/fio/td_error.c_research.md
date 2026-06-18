# sources/test-tools/fio/td_error.c

## Purpose
`td_error.c` implements fio thread error classification, default non-fatal error selection, and aggregate error counting.

## Important APIs, Types, and Functions
`td_error_type(enum fio_ddir ddir, int err)` maps `EILSEQ` to verification errors, read directions to read errors, and all other directions to write errors. `td_non_fatal_error(struct thread_data *td, enum error_type_bit etype, int err)` decides whether an error should be ignored/continued based on `td->o.continue_on_error` and `td->o.ignore_error`. If no explicit ignore list exists for an error type, it installs the static default list `{ EIO, EILSEQ }`. `update_error_count()` increments `td->total_err_count` and records the first error.

## Control Flow and State
The only file-local persistent state is `__NON_FATAL_ERR`. `td_non_fatal_error()` mutates `thread_options.ignore_error[etype]` and `ignore_error_nr[etype]` when defaults are needed. Error counts live in `struct thread_data`.

## Dependencies and Integration Points
The file includes `fio.h`, `io_ddir.h`, and `td_error.h`. It is consumed by fio I/O, verify, and error handling paths that need to distinguish read/write/verify error policies.

## Risks and Test Signals
Risks include the default ignore list being shared static memory, all non-read/non-verify directions mapping to write, and callers needing a valid `etype` index. Test signals are `continue_on_error` behavior, `ignore_error` option behavior, first-error reporting, and zbd tests that expect recovery/continue behavior.
