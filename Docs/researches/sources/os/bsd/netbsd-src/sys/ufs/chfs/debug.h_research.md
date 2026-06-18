# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/debug.h

Purpose: Defines CHFS debugging, warning, notice, and assertion macros.

Key definitions:
- Prefix strings for error, warning, notice, generic debug, EBH debug, and GC debug.
- `unlikely(x)` using GCC `__builtin_expect`.
- `debug_msg(pref, fmt, ...)`: prints prefixed function-name debug output.
- `chfs_assert(expr)`: prints assertion failure information without panicking.
- `chfs_err`, `chfs_warn`, `chfs_noti`, `dbg`, `dbg2`, `dbg_ebh`: enabled or disabled depending on `DBG_MSG`.
- `dbg_gc`: controlled separately by `DBG_MSG_GC`.

Important behavior:
- Errors/warnings/notices print even when `DBG_MSG` is not defined.
- Generic debug macros become no-ops unless debug is enabled.
- GC debug is separately gated.

Dependencies:
- Assumes kernel `printf` and compiler support for variadic macros.

Research notes:
- The `dbg2` definition under `DBG_MSG` appears malformed: `debug_msg(CHFS_DBG2_PREFIX(fmt, ...)` is missing the comma/parenthesis shape used by the others.
- `chfs_assert` logs but does not stop execution.
