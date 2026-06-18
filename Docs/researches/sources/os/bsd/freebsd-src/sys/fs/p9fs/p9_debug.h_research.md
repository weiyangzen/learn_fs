# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_debug.h

This header defines p9fs debug logging flags and the `P9_DEBUG()` macro.

Key details:
- `p9_debug_level` is an external integer controlled elsewhere by sysctl.
- Debug categories:
  - `P9_DEBUG_TRANS`: transport tracing.
  - `P9_DEBUG_SUBR`: p9fs driver submission/subroutine tracing.
  - `P9_DEBUG_LPROTO`: low-level protocol tracing.
  - `P9_DEBUG_PROTO`: high-level protocol tracing.
  - `P9_DEBUG_VOPS`: vnode operation tracing.
  - `P9_DEBUG_ERROR`: verbose error messages.
- `P9_DEBUG(category, fmt, ...)` prints only when the corresponding `P9_DEBUG_<category>` bit is set.

Research-relevant notes:
- The category argument is token-pasted, so callers use `P9_DEBUG(PROTO, ...)`, not numeric values.
- Logging uses `printf()` directly and is synchronous kernel debug output.
