# sources/user-network-fs/samba/source3/smbd/notifyd/notifyd_db.h

## Purpose
This header declares the notifyd database walking interface used by tests and inspection utilities.

## Important APIs, Types, and Functions
The single exported function is `notify_walk(struct messaging_context *msg_ctx, bool (*fn)(...), void *private_data)`. The callback receives the watched path, client server id, notify instance, and caller-private data.

## Control Flow
Callers provide a messaging context connected to the local Samba messaging system. `notify_walk()` handles daemon lookup, database request/response, parsing, and callback iteration.

## State and Persistence
The header owns no state. Callback arguments point into parser-owned data during traversal; callers should copy anything needed beyond the callback lifetime.

## Dependencies and Integration Points
It includes `replace.h` and `notifyd.h`, so users get `NTSTATUS`, `messaging_context`, `server_id`, and `notify_instance` declarations. It is built into the `notifyd_db` subsystem.

## Risks and Edge Cases
The API does not expose the notifyd log index, so it cannot be used for incremental replication. A callback returning false aborts traversal and maps through dbwrap parse behavior.

## Test Signals
Compilation and linkage are covered by `test_notifyd.c`; runtime behavior is covered by the db visibility torture test.
