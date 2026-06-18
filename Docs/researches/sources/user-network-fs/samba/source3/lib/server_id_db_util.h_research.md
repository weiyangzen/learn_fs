# sources/user-network-fs/samba/source3/lib/server_id_db_util.h

## Purpose
This header exposes the source3 utility function for exclusive registration in a `server_id_db`.

## Important APIs, Types, And Functions
It includes `lib/util/server_id_db.h` and declares `int server_id_db_set_exclusive(struct server_id_db *db, const char *name);`.

## Control Flow
No control flow exists in the header. The return code contract is the implementation's errno-style integer: zero on success, nonzero such as `EEXIST` or lower-level database errors on failure.

## State And Persistence
The header defines no state. The implementation mutates the supplied server ID database.

## Dependencies And Integration Points
Callers must link with `server_id_db_util.c` and the lower-level server-id DB and liveness modules. It is intended for daemon singleton/name ownership logic.

## Risks And Test Signals
Risks are API drift and callers ignoring errno-style failures. Build tests should include this header wherever exclusive registration is used; behavior tests belong to the `.c` file.
