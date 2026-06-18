# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_csmapper.h

Thin public/internal wrapper that aliases charset mapper operations to generic mapper operations.

Key behavior:
- Defines `_citrus_csmapper` as `_citrus_mapper`.
- Maps close, convert, state init, and trait accessors directly to `_citrus_mapper_*`.
- Declares `_citrus_csmapper_open`.
- Defines `_CITRUS_CSMAPPER_F_PREVENT_PIVOT` to disable pivot-chain fallback.

This header keeps charset-specific naming while reusing the generic mapper ABI.
