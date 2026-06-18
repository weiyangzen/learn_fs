# sources/test-tools/fio/oslib/statx.h

Purpose: conditional declarations and stub types for `statx()`.

Important APIs/types: when libc lacks `statx()` but syscall headers exist, includes `<linux/stat.h>` and `<sys/stat.h>`. Without syscall support, defines `STATX_ALL` as `0`, undefines `statx`, and declares an empty `struct statx`. Declares fallback `statx()`.

Control flow and state: no runtime logic.

Dependencies and integration: used with `statx.c` to keep source portable across Linux/libc versions.

Risks: empty `struct statx` is only safe when callers do not inspect fields after a guaranteed failure. Configuration must prevent field use on unsupported platforms.

Test signals: compile matrix and behavior tests for code paths that use file birthtime or extended stat metadata.
