# sources/user-network-fs/nfs-ganesha/src/include/fsal_up.h

Purpose: This header defines FSAL upcalls used by backing filesystems to invalidate or update cache state, grant/announce locks, recall layouts/delegations, notify device changes, and release cache entries.

Important APIs/types/functions: Update flags such as `fsal_up_update_filesize_inc` and invalidation flags such as `FSAL_UP_INVALIDATE_ATTRS`, `CONTENT`, `DIR_CHUNKS`, `CLOSE`, and `PARENT` control cache changes. `struct layoutrecall_spec` scopes layout recalls. `struct fsal_up_vector` stores the upcall vtable plus readiness synchronization. Async wrappers like `up_async_invalidate`, `up_async_update`, `up_async_layoutrecall`, and `up_async_delegrecall` post work to a `fridgethr`.

Control flow: FSALs normally call methods through their export's `up_ops`. Calls are synchronous and intended for notification threads; FSAL method contexts should use delayed execution or async wrappers to avoid illegal re-entry such as recalling layouts from inside layoutget.

State and persistence: Upcall state is mostly transient, but it mutates persistent cache/state-layer views of file attributes, ACLs, layouts, locks, delegations, device IDs, and object liveness. The vector's `up_ready`/`up_cancel` condition protects startup/shutdown readiness.

Dependencies and integration points: Includes `gsh_status.h`, `fsal_api.h`, and `sal_data.h`; integrates FSAL implementations with MDCACHE, state management, pNFS, delegation recall, and async worker infrastructure.

Risks: Calling synchronous upcalls from the wrong stack can deadlock or violate layout/state ordering. Update flags must not modify immutable identity fields. Invalidating too little leaves stale cache; invalidating too much hurts performance or closes active files unexpectedly.

Test signals: Exercise attribute-only and content invalidations, parent invalidation, update increment semantics, lock grant/availability callbacks, delegation recall, layout recall with client specs, notify-device events, async wrapper callbacks, and ready/cancel synchronization.
