# sources/security-integrity/audit-userspace/lib/dso.h

Purpose: Private helper header for controlling symbol visibility inside the shared library.

Important macros: Defines `AUDIT_HIDDEN_START` as `_Pragma("GCC visibility push(hidden)")` and `AUDIT_HIDDEN_END` as `_Pragma("GCC visibility pop")` if not already defined.

Control flow: Preprocessor-only.

State and persistence: No state. Affects compiled shared object symbol visibility.

Dependencies and integration: Used by internal libaudit sources/headers to hide implementation details from the public ABI.

Risks: Incorrect placement can hide intended public symbols or expose internal symbols. Assumes GCC-compatible pragma support.

Test signals: Inspect `nm -D`/ABI symbol lists and compile with compilers used by supported platforms.
