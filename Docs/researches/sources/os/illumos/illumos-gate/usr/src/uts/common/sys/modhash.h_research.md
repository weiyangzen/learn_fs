# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modhash.h

Purpose: Declares the generic kernel hash table API.

Key abstractions:
- Opaque key/value types: `mod_hash_key_t`, `mod_hash_val_t`.
- Reservation handle: `mod_hash_hndl_t`.
- Opaque hash: `mod_hash_t`.

Key APIs:
- Constructors/destructors for string, pointer, and ID hash tables.
- Extended constructor with custom key destructor, value destructor, hash algorithm, algorithm data, key comparator, and allocation flag.
- Hash lifecycle: destroy, clear.
- Null destructors.
- Operations: insert, replace, remove, destroy key, find, find with callback, walk.
- Reservation operations for preallocation and reserved insert.

Return codes:
- `MH_ERR_NOMEM`, `MH_ERR_DUPLICATE`, `MH_ERR_NOTFOUND`.
- Walker controls: continue or terminate.

Important detail: Reservation APIs allow callers to allocate outside critical paths and then insert with a reserved handle.

Relevance to subset A: Generic kernel utility; used by larger subsystems, including the MDI vHCI cache in this group.
