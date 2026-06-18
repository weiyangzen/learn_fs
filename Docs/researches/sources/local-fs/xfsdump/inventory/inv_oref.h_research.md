# File Research: sources/local-fs/xfsdump/inventory/inv_oref.h

Defines the intended object-reference structure and macros for the unfinished `inv_oref.c` abstraction.

Key contents:
- Object type flags for inventory index, fstab, and storage object.
- Resolution-depth flags for counters, entries, storage-object headers, sessions, streams, mediafiles, and parent/child kinship.
- `invt_oref_t`, which stores fd, resolved counters, resolved entries/session components, parent/child refs, type flags, lock state, and token pointer.
- Macros for initializing/destroying refs, locking, setting resolved fields, accessing counters/entries, and clearing child refs.
- Prototypes for oref resolution functions.

Notable observations:
- Contains multiple macro/name inconsistencies: `cu_sescnt` maps to `oref_sescnt_u.sescnt`, but the union is named `oref_cnt_u`; child/parent macros use `ku_child`/`ku_parent`, while aliases define `ku_invidx`/`ku_stobj`.
- `OREF_ISLOCKED()` appears logically inverted: it returns true when `lockflag` is `0` or `LOCK_UN`.
- Tail section under `#ifdef NOTDEF` contains unrelated/stale XLV oref declarations.
- This header reinforces that the oref layer is incomplete and not the reliable API surface.
