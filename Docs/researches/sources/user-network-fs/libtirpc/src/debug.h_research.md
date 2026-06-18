## sources/user-network-fs/libtirpc/src/debug.h

Purpose: Declares libtirpc debugging globals/functions and defines the `LIBTIRPC_DEBUG` conditional logging macro.

Important APIs and control flow: Exposes `libtirpc_debug_level`, `log_stderr`, `libtirpc_log_dbg`, and `libtirpc_set_debug`. `LIBTIRPC_DEBUG(level, msg)` evaluates the call tuple only when the requested level is enabled. The inline `vlibtirpc_log_dbg` variant accepts a `va_list` and mirrors stderr/syslog routing.

State and persistence: References global state owned by `debug.c`; no storage is created by the header except inline function code in each translation unit.

Dependencies and integration: Included by files that want debug output without taking a hard dependency on syslog details. The macro's tuple style requires callers to write `LIBTIRPC_DEBUG(1, ("format", arg))`.

Risks and test signals: Macro argument style is easy to misuse. The inline function uses `vfprintf` but this header includes `stdarg.h` and `syslog.h`, not `stdio.h`, so transitive include assumptions matter. Tests/builds should compile debug callers with strict warnings and verify disabled logs avoid formatting side effects.
