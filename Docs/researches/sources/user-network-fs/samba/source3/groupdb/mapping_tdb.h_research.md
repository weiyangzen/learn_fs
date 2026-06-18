# sources/user-network-fs/samba/source3/groupdb/mapping_tdb.h

## Purpose
`mapping_tdb.h` declares the TDB implementation entry point for the group mapping backend.

## Important APIs, Types, And Functions
- `groupdb_tdb_init()` returns a pointer to a static `struct mapping_backend` after ensuring the TDB database is initialized.

## Control Flow
Consumers call `groupdb_tdb_init()` during backend initialization. The implementation opens the database and returns NULL on failure, or the function table on success.

## State And Persistence
The header stores no state. The declared function initializes persistent state in `group_mapping.tdb` through the implementation file.

## Dependencies And Integration Points
It depends on `struct mapping_backend` from `mapping.h`. `mapping.c` uses this declaration to bind the default group mapping backend.

## Risks
The header intentionally exposes only the initializer, so all backend behavior depends on the static function table remaining complete and compatible with `mapping.h`.

## Test Signals
Build tests should verify include ordering with `mapping.h`, and runtime tests should verify NULL return on database initialization failure and non-NULL table on success.
