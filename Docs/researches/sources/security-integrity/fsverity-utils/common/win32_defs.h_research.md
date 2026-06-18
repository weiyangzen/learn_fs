# sources/security-integrity/fsverity-utils/common/win32_defs.h

Purpose: This compatibility header supplies Windows or non-POSIX definitions needed to compile shared code paths where Linux/GNU symbols are unavailable.

Important APIs and macros: It defines fallback `O_BINARY`, `ENOPKG`, cold/printf attributes, fixed-format integer macros, and minimal compatibility types or annotations under `_WIN32`.

Control flow and state: All behavior is preprocessor controlled. No runtime state is stored.

Dependencies and integration points: Included by common project headers to keep library portions buildable in non-Linux userspace contexts, especially tooling that computes or signs digests without kernel ioctls.

Risks and test signals: Risk lies in masking platform limitations: digest/signing can be portable, but enable/measure ioctls remain Linux-specific. Compile-only CI on Windows-like toolchains and absence of attribute-related warnings are the main signals.
