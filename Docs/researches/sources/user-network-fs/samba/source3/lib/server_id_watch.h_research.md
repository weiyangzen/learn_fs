# sources/user-network-fs/samba/source3/lib/server_id_watch.h

## Purpose
This header declares the asynchronous server-id watch API used to wait for process death through tevent.

## Important APIs, Types, And Functions
It includes tevent, talloc, and generated `server_id` definitions. `server_id_watch_send()` starts the request, and `server_id_watch_recv()` completes it and can return the watched `server_id`.

## Control Flow
The header encodes the standard tevent send/recv pattern but has no executable control flow.

## State And Persistence
It defines no persistent state. State is private to the implementation's request object.

## Dependencies And Integration Points
Callers must run a tevent loop and link with the implementation plus server-id liveness support.

## Risks And Test Signals
Header-level risks are API mismatch with the implementation and missing tevent/talloc includes in callers. Functional tests belong with `server_id_watch.c`.
