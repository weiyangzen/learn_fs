# sources/test-tools/strace/src/iopl.c

Purpose: minimal decoder for the `iopl` syscall, printing the requested I/O privilege `level`.

Important APIs/types/functions: `SYS_FUNC(iopl)`, `tprints_arg_name`, `PRINT_VAL_D`, and `RVAL_DECODED`.

Control flow: the decoder names argument 0 as `level`, prints it as a signed integer after casting from `tcp->u_arg[0]`, and reports that the syscall is fully decoded.

State and persistence behavior: no persistent state and no tracee memory access; it only formats one register argument.

Dependencies and integration points: depends on `defs.h` syscall-decoder macros and is selected by the strace syscall table for architectures exposing `iopl`.

Risks: the only meaningful risk is argument signedness/width drift if a future ABI changes the representation; there is no entry/exit split to validate return-time state.

Test signals: tests should assert `iopl(level)` prints a named signed `level` argument and does not emit raw undecoded arguments.
