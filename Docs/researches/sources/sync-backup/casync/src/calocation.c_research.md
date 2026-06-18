# sources/sync-backup/casync/src/calocation.c

## Purpose
Implements `CaLocation`, an immutable/reference-counted descriptor for a position within a serialized filesystem tree or a void blob. Locations support cache keys, archive seek/resume, origin reopening for reflinks, string formatting/parsing, range advancement/merge, and stale-file validation.

## Important APIs, Types, and Functions
Core lifecycle is `ca_location_new`, `ca_location_copy`, `ca_location_ref`, and `ca_location_unref`. `ca_location_format_full` and `ca_location_parse` convert between objects and strings. Patch/update helpers include `ca_location_patch_size`, `ca_location_patch_root`, `ca_location_advance`, and `ca_location_merge`. `ca_location_open` reopens the origin and validates freshness. `ca_location_id_make` hashes a location into a `CaChunkID`, and `ca_location_equal` compares selected fields.

## Control Flow
Construction rejects absolute paths, invalid designators, `UINT64_MAX` offsets, zero sizes, invalid void paths, and overflow. Formatting emits `<path>+<designator><offset>[:size][@inode.mtime[.generation]][%features][#archive-offset][$name-table]`. Parsing strips optional suffixes in reverse order and recreates name-table state when present. Patch/advance/merge functions preserve immutability by modifying in place only when `n_ref == 1`, otherwise copying first.

## State and Persistence Behavior
Locations store relative path, designator, offset, optional size/root, mtime/inode/generation freshness markers, feature flags, archive offset, optional name table chain, and cached formatted string. `ca_location_open` uses either root fd plus `openat` or root path plus `open`, refuses invalidated roots, and returns `-ESTALE` if inode, max(mtime, ctime), or generation no longer match.

## Dependencies and Integration Points
Depends on `CaFileRoot`, `CaNameTable`, `CaDigest`, `ReallocBuffer`, Linux `FS_IOC_GETVERSION`, and utility/time helpers. Used by encoder, sync cache management, and reflink/origin tracking.

## Risks
String parsing is delimiter-sensitive, so path rules forbid absolute paths but still rely on `+` as the final separator. Reopen validation cannot catch every mutation if generation is unavailable and timestamp/inode resolution is insufficient. `ca_location_merge` only merges adjacent ranges with identical root/path/designator/freshness fields.

## Test Signals
Format/parse round trips with all optional suffixes, invalid input rejection, copy-on-write behavior under shared refs, advance and merge boundaries, root fd/path open, invalidated roots, stale detection after file replacement/modification, and location ID stability are key tests.
