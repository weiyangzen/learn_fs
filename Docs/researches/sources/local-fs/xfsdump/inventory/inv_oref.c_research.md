# File Research: sources/local-fs/xfsdump/inventory/inv_oref.c

Appears to be an unfinished alternate “object reference” abstraction for lazily resolving fstab, inventory index, and storage-object structures.

Intended responsibilities:
- Resolve object type (`INVIDX`, `FSTAB`, `STOBJ`) and resource depth (counters, entries, headers, sessions, streams, mediafiles).
- Cache loaded structures in an `invt_oref_t`.
- Synchronize counters/entries back to disk.
- Resolve child storage objects from index entries.
- Create new inventory index and storage objects through oref state.

Important dependencies:
- Uses `inv_oref.h` macros and `inv_priv.h` storage helpers.
- Intended to replace or abstract parts of `inv_idx.c`/`inv_mgr.c`.

Notable observations:
- This file does not look buildable as written: calls like `OREF_ISRESOLVED(INVT_OTYPE_STOBJ)` omit the object argument; symbols such as `oref`, `OREF_CNT`, `OREF_CHILD`, `fd`, `stobj`, `tok`, `rval`, and `invfd` are used inconsistently or undeclared.
- Function calls to `fstab_get_fname()` omit the `forwhat` argument required by `inv_priv.h`.
- Several storage-object resource resolvers referenced by `oref_resolve_upto()` are not implemented in this file.
- Best classified as stale/dead experimental code rather than active inventory logic.
