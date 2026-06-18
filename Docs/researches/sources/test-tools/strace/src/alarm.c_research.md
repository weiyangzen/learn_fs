# sources/test-tools/strace/src/alarm.c

Purpose: simple decoder for the `alarm` syscall.

Important APIs/types/functions: `SYS_FUNC(alarm)`, `tprints_arg_name`, and `PRINT_VAL_U`.

Control flow: prints the single `seconds` argument as an unsigned integer and returns `RVAL_DECODED`.

State and persistence behavior: none.

Dependencies and integration points: linked into `libstrace.a` and referenced by syscall tables for architectures exposing `alarm`.

Risks: minimal; value truncation to `unsigned int` mirrors the syscall argument semantics expected by the decoder.

Test signals: tracing `alarm(2)` should print `seconds=<value>` and decoded return value.
