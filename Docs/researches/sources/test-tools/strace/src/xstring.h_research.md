# sources/test-tools/strace/src/xstring.h

Purpose: `xstring.h` provides checked string-formatting helpers for fixed buffers used in strace support code. The helpers turn unexpected `snprintf` errors, truncation, and pointer-position mistakes into fatal diagnostics.

Important APIs/types/functions: `xsnprintf_` is the inline implementation behind `xsnprintf`; `xsprintf` formats into an array-sized buffer; `get_pos_diff_` validates append positions; and `xappendstr` appends formatted text at an existing buffer position. The header depends on `<stdarg.h>`, `<stdio.h>`, `error_prints.h`, and `macros.h`, including `MUST_BE_ARRAY`.

Control flow: `xsnprintf_` builds a `va_list`, calls `vsnprintf`, then dies through `error_msg_and_die` if the return is negative or would exceed the supplied buffer. `xsprintf` calculates buffer size with `sizeof` plus the array check. `get_pos_diff_` rejects pointer arithmetic overflow, positions beyond the buffer, and positions before the buffer. `xappendstr` computes remaining capacity from the validated position, calls `xsnprintf`, and returns the updated position.

State/persistence behavior: these are inline/macro helpers with no stored state and no persistence. They enforce local buffer invariants at call sites and terminate on invariant violations.

Dependencies and integration points: integrated into decoders and support utilities that assemble short diagnostic or formatted strings in stack buffers. `MUST_BE_ARRAY` intentionally rejects pointer-only buffers for `xsprintf`/`xappendstr`, which protects against accidental `sizeof(pointer)` capacity bugs.

Risks: these helpers are fatal on truncation, so they are appropriate only when the caller has sized the buffer to make truncation a programming error. The macros stringify arguments for diagnostics; complex expressions may produce verbose error messages but are still evaluated once through the underlying call.

Test signals: compile-time array checks, static format checking through `ATTRIBUTE_FORMAT`, tests that append multiple segments without overflow, and negative tests for undersized buffers or invalid positions validate the helper contract.
