# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv_local.h

Internal ABI for Citrus iconv modules.

Key contents:
- Defines getops naming/declaration macros and ops-table construction macro.
- Declares function pointer typedefs for shared init/uninit, context init/uninit, and conversion.
- Defines `_citrus_iconv_ops` with ABI version, shared/context lifecycle, and conversion function.
- Sets `_CITRUS_ICONV_ABI_VERSION` to 2.
- Defines `_citrus_iconv_shared`, including cache linkage, module handle, use count, closure, and conversion name.
- Defines per-open `_citrus_iconv` context with shared pointer and closure.

This is the binary contract consumed by dynamically loaded iconv modules.
