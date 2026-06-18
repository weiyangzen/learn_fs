# sources/user-network-fs/samba/source3/include/idmap.h

## Purpose
`idmap.h` defines the winbind idmap module interface for mapping Unix IDs to SIDs and SIDs to Unix IDs.

## Important APIs, Types, And Functions
- `SMB_IDMAP_INTERFACE_VERSION` is `6`, indicating init callbacks take `TALLOC_CTX` through the current module loading convention.
- `struct idmap_domain` describes a configured domain with name, optional SID, methods, user query callback, low/high id range, read-only flag, and private backend data.
- `struct idmap_methods` defines backend callbacks: `init`, `unixids_to_sids`, `sids_to_unixids`, and `allocate_id`.
- Includes generated `winbindd/idmap_proto.h`.

## Control Flow
Winbind loads an idmap backend, initializes an `idmap_domain`, and calls mapping methods for batches of `id_map` entries. Allocation requests call `allocate_id()` unless the domain is read-only or backend policy rejects it.

## State And Persistence
The header defines runtime domain state; actual persistent mappings live in backend databases or external directory services. The `private_data` pointer is backend-owned.

## Dependencies And Integration Points
It depends on generated idmap NDR types, winbind user info, SID types, and NTSTATUS. Backends must match the interface version.

## Risks
`dom_sid` may not be initialized in all request paths, as the comment warns. Range checks and read-only enforcement are backend-critical. Module ABI drift requires version checks.

## Test Signals
Test backend version compatibility, domain range enforcement, batch mapping partial success/failure, read-only allocation rejection, missing `dom_sid` behavior, and private data cleanup.
