# sources/test-tools/strace/src/print_timespec.h

Purpose: Macro-templated implementation for printing kernel `timespec`-like structures in several generated variants. Including files define `TIMESPEC_T` and macros such as `PRINT_TIMESPEC`, `SPRINT_TIMESPEC`, `PRINT_TIMESPEC_UTIME_PAIR`, or `PRINT_ITIMERSPEC` before including this header.

Important APIs/types/functions: `TIMESPEC_TO_SEC_NSEC` normalizes signed nanoseconds with `zero_extend_signed_to_ull`; `print_timespec_t` emits `{tv_sec, tv_nsec}` or an alternate `TIMESPEC_NSEC` field; optional public wrappers include memory-size decoders, pointer decoders, string formatter, utime-pair printer, and itimerspec printer.

Control flow: all pointer printers fetch tracee memory through `umove_or_printaddr` or `umove`; unavailable or too-short inline buffers print `tprint_unavailable`. `SPRINT_TIMESPEC` returns `NULL`, an address, or decoded text depending on address, verbosity, syscall phase, and read success. Utime pair decoding recognizes `UTIME_NOW` and `UTIME_OMIT` and switches output style according to xlat verbosity.

State and persistence: only the string formatter uses a static buffer, so results are transient and overwritten by the next call. No persistent tracee state is modified.

Dependencies/integration: depends on `defs.h`-style print helpers, `xstring.h`, `sprinttime_nsec`, `print_local_array`, and MPERS/architecture wrappers that define the macro names. It is integrated by `print_timespec32.c` and `print_timespec64.c`.

Risks: as a macro-included implementation, symbol names and struct field aliases must be defined consistently by includers. The static string buffer is not reentrant. `void *` arithmetic in array decoding relies on compiler extensions used by strace. Correct handling of `UTIME_*` depends on kernel constants matching fallback definitions.

Test signals: compare decoded `utimensat`, `clock_gettime`, timer, and itimerspec outputs across abbrev/raw/verbose xlat modes; exercise failed `umove`, null address, short data-size buffers, and 32/64-bit personalities.
