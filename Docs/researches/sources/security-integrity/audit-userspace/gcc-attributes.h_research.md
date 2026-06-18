# sources/security-integrity/audit-userspace/gcc-attributes.h

Purpose: Private compatibility header that supplies fallback definitions for GCC/glibc function-attribute macros and branch prediction helpers when libc headers do not provide them.

Important macros: Defines `__has_attribute`, `__attr_access`, `__attribute_malloc__`, `__attr_dealloc`, `__attr_dealloc_free`, `__attribute_const__`, `__attribute_pure__`, `__nonnull`, `__wur`, `likely`, and `unlikely` if missing.

Control flow: Preprocessor-only header guarded by `AUDIT_GCC_ATTRIBUTES_H`. It conditionally defines macros to no-ops or `__builtin_expect` expressions.

State and persistence: No state. Affects compile-time diagnostics, analyzer annotations, and optimization hints.

Dependencies and integration: Intended for internal sources that need portability across glibc and non-glibc libc implementations such as musl. Comments explicitly prohibit including it from public API headers (`audit-records.h`, `audit_logging.h`, `auparse-defs.h`, `auparse.h`, `auplugin.h`, `libaudit.h`) because it is not shipped.

Risks: If public headers accidentally depend on this private file, installed development packages break. No-op fallbacks reduce static analyzer coverage on platforms without native attributes. `likely`/`unlikely` assume GCC-compatible builtins.

Test signals: Build on glibc and musl-like environments, confirm public headers compile standalone after installation, and run compiler warning tests for attribute probes in `configure.ac`.
