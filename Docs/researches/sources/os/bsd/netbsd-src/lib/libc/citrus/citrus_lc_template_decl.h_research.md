# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_template_decl.h

Declaration companion for the generic Citrus locale template.

Key behavior:
- Includes `nb_lc_template_decl.h`.
- Declares category-specific `_PREFIX(init_normal)` and `_PREFIX(init_fallback)` inline functions expected by `citrus_lc_template.h`.

This header defines the required hooks each locale category implementation must provide.
