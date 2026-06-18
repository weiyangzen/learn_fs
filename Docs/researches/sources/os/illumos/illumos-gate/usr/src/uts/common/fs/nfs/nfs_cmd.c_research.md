# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_cmd.c

## Purpose

`nfs_cmd.c` implements kernel-side support for NFS daemon commands delivered through a per-zone door. In this file, the main consumer is export character-set mapping: the kernel asks userland, normally `mountd`, whether a specific exported path and client address require filename character-set conversion.

The file also caches positive and negative character-map lookup results in `exportinfo_t`, then applies `kiconv` conversions to individual names and directory entries.

## Main Interfaces

Door and lifecycle interfaces:

- `nfscmd_args`
- `nfscmd_init`
- `nfscmd_fini`
- `nfscmd_send`

Character-map interfaces:

- `nfscmd_findmap`
- `nfscmd_charmap`
- `nfscmd_insert_charmap`
- `nfscmd_convname`
- `nfscmd_convdirent`
- `nfscmd_convdirplus`
- `nfscmd_countents`
- `nfscmd_dropped_entrysize`

Per-zone state is held in `nfscmd_globals_t`, which contains a mutex and a `door_handle_t`.

## Door Handling

`nfscmd_args()` installs or replaces the per-zone door handle from a door id supplied through the NFS command interface. Existing handles are released with `door_ki_rele()`.

`nfscmd_send()` sends an `nfscmd_arg_t` to the door and reads an `nfscmd_res_t` response. It handles several failure modes:

- If no door has been registered, it retries for `NFSCMD_DR_TRYCNT` iterations before returning `NFSCMD_ERR_DROP`.
- `EAGAIN` sleeps and retries.
- `EINTR` checks whether the door was revoked. If revoked, it clears the cached handle and retries so SMF can restart the daemon and register a new door.
- Stale handles or unexpected errors get one final retry before returning `NFSCMD_ERR_FAIL`.

The function holds a reference on the door while issuing the upcall so concurrent replacement cannot free the handle prematurely.

## Character-Set Cache

`nfscmd_findmap()` first checks whether the export has `EX_CHARMAP`. If not, it is a no-op. If charset mapping is enabled, it searches `exi->exi_charset` for a cached client-address entry.

On cache miss, `nfscmd_charmap()` asks userland for a mapping using `NFSCMD_CHARMAP_LOOKUP`, passing the export path and client address. It then inserts either:

- A positive mapping with `inbound = kiconv_open("UTF-8", name)` and `outbound = kiconv_open(name, "UTF-8")`
- A negative cache entry with null converters when lookup fails

This means both “mapping exists” and “mapping does not exist” are cached per export/client pair.

## Name Conversion

`nfscmd_convname()` converts a single name buffer. If `inbound` is true, it converts from the client code set into UTF-8. Otherwise it converts from UTF-8 to the client code set. If no mapping exists, or the relevant converter is unavailable, it returns the original name pointer. If conversion fails, it frees the temporary buffer and returns `NULL`.

`nfscmd_convdirent()` handles a single `dirent64` record. It copies the fixed part of the dirent, converts the name with the outbound converter, recomputes `d_reclen`, and returns either the converted buffer, the original buffer, or `NULL`. If conversion fails due to `E2BIG`, it can report `NFS3ERR_NAMETOOLONG`.

`nfscmd_convdirplus()` converts a sequence of directory entries into a new buffer bounded by `maxsize`. Entries that fail with `EILSEQ` are skipped. The return value is the number of entries represented after conversion and skipped-entry accounting, while `*ndata` points at the new buffer.

## Directory Helpers

`nfscmd_countents()` walks a `dirent64` buffer using `d_reclen` and counts entries.

`nfscmd_dropped_entrysize()` computes how many bytes would be removed from the tail of a directory-entry buffer if a given number of entries were dropped. This supports fitting converted directory data into protocol response limits.

## Notable Invariants

- Door handles are per-zone.
- Character-map cache entries are per export and client address.
- Negative character-map results are cached to avoid repeated userland upcalls.
- Returned converted names may be newly allocated or may be the original pointer, so callers must understand ownership.
- Directory conversion must preserve `dirent64` layout and recompute record lengths after name conversion.

## Dependencies

This file depends on:

- Door kernel interfaces: `door_ki_lookup`, `door_ki_hold`, `door_ki_rele`, `door_ki_upcall`, `door_ki_info`
- Export structures from `nfs/export.h`
- NFS command definitions from `nfs/nfs_cmd.h`
- Kernel iconv APIs: `kiconv_open`, `kiconv`
- `dirent64` layout and NFSv3 status definitions

## Research Notes

The main correctness concerns are retry behavior around revoked doors, lifetime/ownership of converted name buffers, bounds handling in directory conversion, and the use of cached negative charset mappings. This file participates in NFS server/export behavior rather than the NFS client vnode path.
