# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype.c

Runtime loader and dispatcher setup for Citrus ctype encoding modules.

Key behavior:
- Defines `_citrus_ctype_default` using the built-in default `NONE` ctype ops.
- In dynamic builds, `_citrus_ctype_open` loads an i18n module unless the encoding is default.
- `_initctypemodule` resolves the module's ctype getops symbol, copies ops, patches missing ABI v1/v2 functions with fallback shims, validates required methods, and initializes module closure.
- `_citrus_ctype_close` uninitializes and unloads non-default modules.
- In non-dynamic builds, only the default ctype is accepted.

Important contract:
- The file enforces `_CITRUS_CTYPE_ABI_VERSION` compatibility and shields older modules with fallback implementations.
