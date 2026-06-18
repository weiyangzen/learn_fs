# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/unistd.h

Read completely: 75 lines.

This compatibility header declares old and compatibility-visible process/file-descriptor interfaces: `vfork`, `__vfork14`, `dup3`, and `__dup3100`. It wraps declarations in `__BEGIN_DECLS`/`__END_DECLS` and marks the vfork variants `__returns_twice`.

Important interactions: consumed by compatibility implementations such as `compat_dup3.c`, and by legacy code that intentionally binds to older libc symbol versions.

Security/reliability notes: declaration-only; the main risk is ABI confusion if included instead of the current public `<unistd.h>`.
