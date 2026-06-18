# sources/user-network-fs/samba/source3/groupdb/mapping.h

## Purpose
`mapping.h` defines the storage key constants and backend abstraction for Samba3 group mapping. It is the contract between passdb-facing group mapping code and concrete persistence implementations such as the TDB backend.

## Important APIs, Types, And Functions
- `DATABASE_VERSION_V1` and `DATABASE_VERSION_V2` document historic database versions.
- `GROUP_PREFIX` / `GROUP_PREFIX_LEN` identify records keyed by `UNIXGROUP/<sid>`.
- `MEMBEROF_PREFIX` / `MEMBEROF_PREFIX_LEN` identify reverse alias membership records keyed by `MEMBEROF/<member-sid>`.
- `struct mapping_backend` contains function pointers for initialization, group map add/get/remove/enum, alias membership lookup, add/delete, and member enumeration.

## Control Flow
The header itself has no control flow. Runtime code loads one `mapping_backend` and calls through these function pointers. The reverse-membership design means "which aliases is this SID a member of?" can be answered by one record fetch, while enumerating all members of an alias requires traversal.

## State And Persistence
The constants define on-disk key namespaces used by group mapping stores. Values are backend-defined, but the TDB backend stores packed gid/type/name/comment for group records and space-separated alias SIDs for member-of records.

## Dependencies And Integration Points
The contract depends on `GROUP_MAP`, `dom_sid`, `lsa_SidType`, `gid_t`, `TALLOC_CTX`, and `NTSTATUS` from Samba headers. It is consumed by `mapping.c` and implemented by `mapping_tdb.c`.

## Risks
Changing prefixes or lengths breaks existing databases. Adding function pointers changes backend ABI inside the source tree and requires all implementations to update. Reverse membership optimizes session setup but makes alias member enumeration traversal-heavy.

## Test Signals
Tests should verify exact key prefixes, backend implementations covering every function pointer, and compatibility when reading existing TDB records keyed with these constants.
