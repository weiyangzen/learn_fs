# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_namespace.h

Read completely: 238 lines.

This header is the Citrus libc namespace indirection layer. It maps short internal symbols such as `_mapper_open`, `_stdenc_mbtowc`, `_region_peek32`, and `_index_t` onto exported/private `_citrus_*` names unless a component-specific `_CITRUS_*_NO_NAMESPACE` macro disables that remapping.

The file covers alias lookup, BCS helpers, csmapper, database and database factory APIs, lookup/esdb/hash helpers, mapper APIs and result constants, memstream/mmap helpers, pivot factory conversion, region helpers, standard encoding APIs and state constants, and basic Citrus integer types. It has no executable logic, but it determines the symbol names seen by all modules that include it.

Important interactions: most files in this group include it before using shorthand helpers. If a module defines a `_NO_NAMESPACE` macro inconsistently, it can silently change which symbol names are referenced at compile time.

Security/reliability notes: no direct runtime attack surface. Its main risk is ABI/symbol confusion, especially because it remaps both function-like names and type/constant names.
