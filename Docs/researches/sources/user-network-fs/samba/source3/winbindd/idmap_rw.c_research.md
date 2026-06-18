# sources/user-network-fs/samba/source3/winbindd/idmap_rw.c

## Purpose
This file implements the backend-independent "allocate and store a new mapping" sequence used by writable idmap backends. It centralizes type validation, allocation calls, storage calls, and collision retry behavior.

## Important APIs, Types, And Functions
The exported function is `idmap_rw_new_mapping(struct idmap_domain *dom, struct idmap_rw_ops *ops, struct id_map *map)`. `struct idmap_rw_ops` is declared in `idmap_rw.h` and supplies `get_new_id` and `set_mapping`.

## Control Flow
The function validates `map` and `map->sid`. If the requested type is `ID_TYPE_NOT_SPECIFIED` or `ID_TYPE_BOTH`, it sets `map->status = ID_REQUIRE_TYPE` and returns `NT_STATUS_SOME_NOT_MAPPED`, requiring the caller/parent to supply a UID/GID hint. UID and GID requests call `ops->get_new_id`, mark the map as mapped, then call `ops->set_mapping`. If storage reports `NT_STATUS_OBJECT_NAME_COLLISION`, the code retries lookup through `dom->methods->sids_to_unixids`.

## State And Persistence
This file owns no persistence. Backend ops perform allocation and storage, typically in TDB or LDAP. The caller is responsible for wrapping the sequence in a transaction where the backend supports it.

## Dependencies And Integration
It depends on idmap domain methods, SID string helpers, and backend-provided `idmap_rw_ops`. `idmap_tdb_common`, `idmap_ldap`, and autorid-related code use this abstraction.

## Risks And Test Signals
Test null inputs, `ID_TYPE_NOT_SPECIFIED`, `ID_TYPE_BOTH`, UID/GID allocation success, allocation failure, set failure, collision retry, and caller transactions. The collision path recursively uses the domain's `sids_to_unixids`; tests should ensure this does not re-enter allocation indefinitely.
