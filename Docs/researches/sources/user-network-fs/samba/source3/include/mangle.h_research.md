# sources/user-network-fs/samba/source3/include/mangle.h

## Purpose
`mangle.h` declares the pluggable 8.3 filename mangling interface used when SMB clients require DOS-compatible names. It abstracts the algorithm that detects, looks up, and generates mangled names for a share.

## Important APIs, Types, And Control Flow
`struct mangle_fns` is a callback table. `reset()` clears algorithm state. `is_mangled()` detects existing mangled names. `must_mangle()` decides whether a long name must be converted. `is_8_3()` validates DOS 8.3 form with case and wildcard options. `lookup_name_from_8_3()` maps a mangled input back to the long name, allocating with talloc. `name_to_8_3()` emits a 13-byte output buffer, with cache control, default case, and share parameters.

## State And Persistence
The header defines no storage, but the callback table permits implementations to keep caches or persistent mapping databases elsewhere. The `cache83` argument and reverse lookup API imply stateful name mapping when deterministic conversion alone cannot recover the long name.

## Dependencies And Integration Points
It depends on `TALLOC_CTX`, `share_params`, and Samba filename matching/case rules. It integrates with directory enumeration, path lookup, SMB1 clients, share configuration, and any module selected as the active mangling backend.

## Risks And Test Signals
Risks include collisions between long names, case sensitivity mismatches, wildcard handling differences, invalid output buffer length assumptions, and stale reverse lookup cache entries. Test signals include 8.3 validation cases, long-name collision generation, cache-enabled and cache-disabled reverse lookup, wildcard patterns, per-share case settings, SMB1 directory listings, and cross-platform names containing characters illegal in DOS aliases.
