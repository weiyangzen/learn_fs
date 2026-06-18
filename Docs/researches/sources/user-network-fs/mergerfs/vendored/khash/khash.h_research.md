<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/khash/khash.h -->
# sources/user-network-fs/mergerfs/vendored/khash/khash.h

Purpose: This is Attractive Chaos' macro-generated C hash table implementation. It provides typed hash maps and sets through `KHASH_INIT`, `KHASH_DECLARE`, `KHASH_MAP_INIT_INT`, `KHASH_MAP_INIT_STR`, and related convenience macros.

Important APIs and types: `khash_t(name)` expands to a struct containing bucket counts, occupancy, flags, keys, and optional values. Public macros wrap generated functions such as `kh_init`, `kh_destroy`, `kh_clear`, `kh_resize`, `kh_put`, `kh_get`, `kh_del`, `kh_exist`, `kh_key`, `kh_val`, `kh_begin`, `kh_end`, and iteration helpers. Built-in hash/equality functions cover 32-bit ints, 64-bit ints, and NUL-terminated strings.

Control flow and state: flags store two bits per bucket for empty/deleted/live state. Lookup and insertion use power-of-two bucket counts and quadratic probing. `kh_put` grows or cleans deleted entries when `n_occupied` reaches the 0.77 upper bound; `kh_resize` rehashes live entries and may shrink arrays. State is entirely heap-resident behind overridable `kcalloc`, `kmalloc`, `krealloc`, and `kfree` macros.

Risks and test signals: tables are not thread-safe, string keys are compared by content but not owned/copied, and allocation failures are reported through `ret = -1` or resize return values that callers must check. Macro expansion can hide type mistakes. Tests should cover insertion, duplicate insert return codes, deletion/tombstone reuse, resize growth/shrink, string-key lifetime assumptions, and allocation-failure behavior if custom allocators are used.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/khash/khash.h -->
