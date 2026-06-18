# File Research: sources/os/bsd/freebsd-src/sys/sys/tslog.h

Optional kernel timestamp logging macro header.

Key responsibilities:
- Defines event kind constants for enter, exit, thread, and event records.
- Provides convenience macros for function entry/exit, named events, source line events, wait/unwait/hold/release events, fork, exec, namei, and process-exit logging.
- When `TSLOG` is enabled, routes macros to `tslog()` and `tslog_user()` declarations.
- When `TSLOG` is disabled, compiles logging macros away.

Dependencies:
- Kernel-only; under `TSLOG`, includes `_types` and `pcpu` for `pid_t`/current CPU-related context.

Notable risks:
- Because disabled macros become empty statements, callers must not rely on logging expressions for side effects.
- Enabled logging is low-level tracing and must avoid adding unsafe work to sensitive kernel paths.
