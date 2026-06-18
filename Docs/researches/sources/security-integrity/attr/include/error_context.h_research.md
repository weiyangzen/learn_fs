## sources/security-integrity/attr/include/error_context.h

Purpose: callback interface for libattr error reporting and quoting.

`struct error_context` contains `error`, `quote`, and `quote_free` function pointers, with optional macros that null-check callbacks. State is supplied by callers, allowing tools to integrate localized or structured diagnostics. Dependencies are variadic printf contracts. Risks include callback lifetime and varargs format correctness; macro names can shadow other `error` or `quote` symbols when `ERROR_CONTEXT_MACROS` is defined. Test signals are xattr copy failures with and without context callbacks.
