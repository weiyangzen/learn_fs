# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_shortname.c

Purpose: `pvfs_shortname.c` implements 8.3 short-name generation, mangled-name detection, reverse lookup through a prefix cache, and DOS reserved-name checks for the POSIX backend.

Important APIs, types, and functions: Public functions are `pvfs_mangle_init`, `pvfs_short_name_component`, `pvfs_short_name`, `pvfs_mangled_lookup`, `pvfs_is_reserved_name`, and `pvfs_is_mangled_component`. The main state type is `struct pvfs_mangle_context`, containing character flags, mangle prefix/modulus, direct-mapped prefix cache, and base-36 reverse table. Important helpers are `mangle_hash`, `is_mangled_component`, `is_8_3`, `check_cache`, `is_reserved_name`, `is_legal_name`, `name_map`, and `init_tables`.

Control flow: Initialization reads `mangle:cachesize` and `mangle:prefix`, allocates the prefix cache, validates prefix length, and builds character classification tables. `name_map` returns no conversion for valid 8.3 names or legal long names when 8.3 is not required; otherwise it builds a `PREFIX~HASH.EXT` name using uppercase ASCII lead characters, a base-36 FNV-derived hash, and up to three ASCII extension characters. Reverse lookup recognizes mangled syntax, decodes the hash, and returns the cached original prefix plus extension.

State and persistence behavior: The cache is in-memory and direct-mapped, so reverse lookup is opportunistic and can miss after eviction or restart. Short names are not persisted. Reserved-name and legality decisions are deterministic from tables.

Dependencies and integration points: It depends on `pvfs_name_hash`, Samba charset/codepoint helpers for long-name legality, loadparm for mangle settings, and path resolution/search/query code that exposes short names or resolves mangled components.

Risks: The file intentionally uses byte-oriented string routines in many places; replacing them with multibyte helpers can break the algorithm. Hash collisions and direct-map cache eviction mean reverse lookup is not authoritative. Only restricted ASCII is allowed for generated 8.3 names.

Test signals: Cover valid 8.3 pass-through, long-name mangling, reserved DOS names, non-ASCII leading characters, extension handling, wildcard legality, cache lookup/eviction, configurable prefix lengths, and case-insensitive matching of mangled names.
