# File Research: sources/os/bsd/openbsd-src/sys/sys/stdarg.h

Compiler-backed variadic argument definitions.

This header wraps compiler builtins for `__gnuc_va_list`, `va_list`, `va_start`, `va_end`, `va_arg`, `__va_copy`, and C99 `va_copy`. It notes the standard rule that `va_arg` types must match default argument promotions.

Filesystem/storage relevance: generic C infrastructure. It is used by kernel and userland formatted printing/logging paths that filesystem and storage code may call, but it has no filesystem semantics.
