# sources/user-network-fs/samba/source3/smbd/mangle_hash2.c

## Purpose
`mangle_hash2.c` implements the newer hash2 name mangling backend. It produces names of the form `Annnn~n.AAA` using a base-36 FNV1-derived hash, fast ASCII character tables, DOS reserved-name detection, and the global smbd memcache for reverse prefix lookup. It also contains the no-op POSIX mangling backend.

## Important APIs, Types, And Functions
The backend exports `mangle_hash2_init()` and `posix_mangle_init()`. Important constants and tables are `basechars`, `reserved_names`, `char_flags`, `base_reverse`, `FNV1_PRIME`, and `FNV1_INIT`. Hashing and cache helpers are `mangle_hash()`, `cache_insert()`, and `cache_lookup()`. Detection and validation are handled by `is_mangled_component()`, `is_mangled()`, `is_8_3()`, `is_reserved_name()`, `is_legal_name()`, and `must_mangle()`. Forward conversion is `hash2_name_to_8_3()`, and reverse lookup is `lookup_name_from_8_3()`. The POSIX backend functions always report no mangling and return an empty 8.3 output buffer.

## Control Flow
`mangle_hash2_init()` clamps `mangle_prefix` from loadparm into the range 1..6, optionally initializes generated tables when dynamic mode is enabled, resets the backend, and returns the function table. `hash2_name_to_8_3()` first returns legal non-reserved 8.3 names unchanged. Otherwise it chooses an extension only when the suffix is 1..3 ASCII chars, derives leading uppercase ASCII prefix characters, hashes the prefix before the dot, emits base36 hash characters around `~`, appends an uppercased extension, and optionally stores the prefix in `MANGLE_HASH2_CACHE`. Reverse lookup validates that the name matches hash2 shape, decodes the base36 hash, reads the cached prefix from memcache, and appends any extension from the short name.

## State And Persistence
State is process-local. `mangle_prefix` is global and configured at backend initialization. Reverse lookup data is stored in `smbd_memcache()` under `MANGLE_HASH2_CACHE`, keyed by the 31-bit hash value and containing a NUL-terminated prefix. Static character tables are compiled in unless `DYNAMIC_MANGLE_TABLES` is enabled for regeneration. The POSIX backend keeps no state.

## Dependencies And Integration Points
This file depends on global memcache from `globals.c`, loadparm for `mangle prefix`, Samba string/case helpers, and the `mangle_fns` abstraction. `filename.c` relies on the reverse cache to avoid full directory scans for incoming mangled names. Directory listing code uses `name_to_8_3()` via the wrapper layer.

## Risks
Reverse lookup is cache-dependent and hash-only, so collisions can map to the most recently cached prefix. The code intentionally uses byte string operations for performance and must preserve the documented multibyte assumptions. Changes to flag tables require regeneration. Extension parsing is ASCII-only by design. `mangle_prefix` affects the hash space and collision behavior; larger visible prefixes weaken the hash.

## Test Signals
Tests should cover prefix clamping, legal-name pass-through, DOS reserved-name mangling, illegal chars, forced shortname chars, wildcard handling, multibyte names, extension selection rules, cache insertion disabled/enabled, reverse lookup success/miss/collision, exact hash2 pattern detection, path-component detection, table regeneration equivalence, and POSIX backend no-op behavior.
