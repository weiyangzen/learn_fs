# sources/user-network-fs/samba/source3/winbindd/idmap_rw.h

## Purpose
This header declares the abstract read/write idmap operation table and the shared helper for creating a new SID-to-Unix-ID mapping. It lets allocating backends reuse common mapping creation logic while preserving backend-specific storage.

## Important APIs, Types, And Functions
`struct idmap_rw_ops` has `get_new_id` and `set_mapping` callbacks. `idmap_rw_new_mapping` accepts a domain, ops table, and map with `sid` and requested `xid.type`.

## Control Flow
The header documents the required caller contract: invoke the helper from a backend's `sids_to_unixids` implementation, provide a type hint, and handle atomicity externally. No executable code is present.

## State And Persistence
No state is held here. Persistence happens through callback implementations.

## Dependencies And Integration
It depends on `idmap.h` for `struct idmap_domain`, `struct id_map`, `struct unixid`, and `NTSTATUS`. It is used by TDB, LDAP, and autorid allocation flows.

## Risks And Test Signals
ABI/build tests should ensure all writable backends initialize both callbacks before calling the helper. Behavioral tests should verify each backend honors the documented transaction requirement.
