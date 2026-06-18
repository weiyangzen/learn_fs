# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_template.h

Generic Citrus locale category creation template.

Key behavior:
- Builds path `<root>/<name>/_CATEGORY_DB`.
- Maps the category file.
- Allocates category data storage.
- Attempts to open the mapped file as a Citrus DB with `_CATEGORY_MAGIC`.
- If DB open succeeds, calls `_PREFIX(init_normal)`.
- If DB open fails, binds a memory stream and calls `_PREFIX(init_fallback)`.
- Includes NetBSD `nb_lc_template.h` for the rest of category lifecycle logic.

Used by messages, monetary, numeric, and time loaders.
