# sources/user-network-fs/samba/source3/smbd/mangle_hash.c

## Purpose
`mangle_hash.c` implements Samba's legacy hash-based 8.3 name mangling backend. It validates DOS 8.3 legality using UCS2 tables, detects legacy mangled patterns, generates short names using a magic character plus checksum-derived base characters, and stores reverse mappings in an internal TDB.

## Important APIs, Types, And Functions
The backend exports `mangle_hash_init()` and a `struct mangle_fns` with reset, detect, must-mangle, 8.3 validation, reverse lookup, and forward conversion hooks. Core validation functions are `isvalid83_w()`, `has_valid_83_chars()`, `has_illegal_chars()`, `mangle_get_prefix()`, `is_valid_name()`, `is_8_3_w()`, and `is_8_3()`. Detection uses `init_chartest()` and `is_mangled()` to find the configured magic character followed by two valid basechars at component boundaries. Reverse mapping uses `cache_mangled_name()` and `lookup_name_from_8_3()` against `tdb_mangled_cache`. Forward mapping is `to_8_3()` and `hash_name_to_8_3()`. `fast_string_hash()` customizes the internal TDB hash.

## Control Flow
Initialization creates the `chartest` basechar table if needed, opens an internal TDB named `mangled_cache`, and returns the backend function table. `hash_name_to_8_3()` converts input to UCS2, returns it unchanged if it is already legal 8.3, otherwise calls `to_8_3()`, which computes a checksum, uppercases the string, extracts up to five basechars for the prefix, appends the magic character and two checksum chars, and preserves up to three extension chars. The generated mapping is cached for reverse lookup. Reverse lookup first tries the full mangled name, then tries without extension and reattaches the requested extension when a prefix mapping is found.

## State And Persistence
State is in process memory: global `chartest`, global `tdb_mangled_cache`, and the configured magic/default-case values read at call time. The TDB is opened with `TDB_INTERNAL`, so it is not a durable database. The backend reset hook is effectively a no-op and does not clear or reopen the TDB.

## Dependencies And Integration Points
The backend depends on Unicode conversion helpers (`push_ucs2_talloc`, UCS2 string functions), string case helpers, TDB utility functions, loadparm share settings, and global mangling variables. It is selected by `mangle.c` and used by path lookup when clients provide or request DOS 8.3 names.

## Risks
The legacy algorithm has a small checksum space and can collide. `cache_mangled_name()` temporarily modifies the raw-name extension through a discarded const pointer, which is carefully restored but fragile. Reverse lookup depends on cache warmness and can fail, forcing directory scans elsewhere. Validation is UCS2-table based and must match Windows compatibility expectations for reserved names, trailing dots/spaces, wildcards, and illegal characters.

## Test Signals
Tests should cover legal and illegal 8.3 names, reserved DOS device names, trailing dot/space rejection, wildcard allowance toggles, multibyte conversion failures, magic-pattern detection across path components, extension-group reverse cache behavior, checksum collisions, cache disabled/uninitialized lookup, `cache83` false behavior, default upper/lower case behavior, and internal TDB initialization failure paths.
