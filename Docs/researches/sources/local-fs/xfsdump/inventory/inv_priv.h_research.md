# File Research: sources/local-fs/xfsdump/inventory/inv_priv.h

Private inventory header defining the on-disk format, token internals, helper macros, and internal function prototypes.

Key contents:
- Documents the three-level inventory hierarchy: fstab -> per-filesystem inventory index -> storage objects.
- Defines constants for object capacities, flags, permissions, return values, offsets, and locking.
- Defines on-disk structures: `invt_session_t`, `invt_seshdr_t`, `invt_stream_t`, `invt_mediafile_t`, `invt_entry_t`, `invt_counter_t`, `invt_sescounter_t`, and `invt_fstab_t`.
- Defines token structures: inventory token, session token, and stream token.
- Defines reconstruction/query containers: `invt_sessinfo_t`, `invt_idxinfo_t`, `invt_mobjinfo_t`, and `invt_pr_ctx_t`.
- Provides I/O macros over `inv_core.c`.
- Declares internal functions across index, storage-object, fstab, manager, and debug modules.

Important on-disk layout:
- Index/fstab files start with `invt_counter_t`, followed by fixed-size entry arrays.
- Storage objects start with `invt_sescounter_t`, then reserved session headers, session records, then variable stream/mediafile data from `ic_eof`.
- `INVT_STOBJ_MAXSESSIONS` is 5, so storage objects split frequently.

Notable observations:
- Prototypes include some inconsistencies with implementations, notably `init_idb()` return type.
- Public structs in `inventory.h` are distinct from private on-disk structs; conversion lives in `inv_stobj.c`.
