# sources/user-network-fs/samba/source3/include/util_tdb.h

## Purpose
`util_tdb.h` declares source3 utility helpers around Samba's TDB database library, including deprecated packing helpers, logging-aware open, error mapping, data comparison/debug formatting, and timeout-based chain locks.

## Important APIs, Types, and Functions
- Deprecated marshalling: `tdb_unpack`, `tdb_pack`.
- Open/error helpers: `tdb_open_log` and `map_nt_error_from_tdb`.
- Data helpers: `tdb_data_cmp`, `tdb_data_string`, and `tdb_data_dbg`.
- Lock helpers: `tdb_chainlock_with_timeout`, `tdb_lock_bystring_with_timeout`, and `tdb_read_lock_bystring_with_timeout`.

## Control Flow and State
Callers open TDBs through `tdb_open_log`, manipulate `TDB_DATA`, and use timeout lock helpers around critical sections. The header explicitly recommends IDL/NDR instead of the legacy format-string pack/unpack helpers for complex data.

## Persistence Behavior
TDB databases persist Samba runtime state such as locks, shares, profiles, and caches depending on the caller. This header declares utility operations over those persistent databases but does not define a schema.

## Dependencies and Integration Points
It includes `tdb.h`, `talloc.h`, NTSTATUS mapping, and the common `lib/util/util_tdb.h`. It is used by source3 code that stores state in TDB and needs source3-specific logging/error behavior.

## Risks
- Deprecated pack/unpack use can create fragile binary schemas.
- Timeout lock helpers must avoid deadlocks and must report lock failure clearly.
- Debug string helpers must avoid logging untrusted binary data unsafely or leaking sensitive content.

## Test Signals
TDB open/error mapping tests, lock timeout behavior, data comparison/formatting checks, and migration tests away from pack/unpack formats.
