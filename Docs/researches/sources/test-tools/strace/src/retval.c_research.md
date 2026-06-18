# sources/test-tools/strace/src/retval.c

Purpose: Centralizes syscall return-value formatting helpers.

Important APIs/types/functions: return-value printing functions declared in `retval.h`, including numeric, hex, fd, address, decoded/verbose style helpers, and error-aware formatting paths.

Control flow: chooses output representation based on decoder return flags, syscall error state, and global formatting settings. It prints raw return values, symbolic auxiliary text, and error names/comments consistently for all syscall decoders.

State and persistence: consults `struct tcb` syscall result fields and global output options; does not own persistent state.

Dependencies/integration: core syscall dispatch, errno/xlat helpers, fd/path caches where applicable, and all `SYS_FUNC` return flag conventions.

Risks: any change affects every syscall line. Signedness, hex formatting, and error-vs-valid-negative handling are high-risk for regressions.

Test signals: broad syscall golden tests, especially negative valid returns, `RVAL_HEX`, `RVAL_FD`, `RVAL_DECODED`, injected errors, and raw mode.
