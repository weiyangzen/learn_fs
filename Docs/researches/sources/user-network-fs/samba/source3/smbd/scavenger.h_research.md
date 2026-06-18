# sources/user-network-fs/samba/source3/smbd/scavenger.h

## Purpose
This header declares the public smbd scavenger interface for initializing the durable-open cleanup helper and scheduling disconnected opens for later cleanup.

## Important APIs, Types, And Functions
It exposes `bool smbd_scavenger_init(TALLOC_CTX *mem_ctx, struct messaging_context *msg, struct tevent_context *ev)` and `void scavenger_schedule_disconnected(struct files_struct *fsp)`. It intentionally hides `smbd_scavenger_state`, message formats, timer contexts, and cleanup helpers inside `scavenger.c`.

## Control Flow
The header has no runtime control flow. Callers include it to initialize the message handler during smbd setup and to schedule cleanup when a durable open transitions to disconnected.

## State And Persistence
No state lives in the header. The declared functions mutate runtime scavenger state and eventually persistent locking/open databases as described in `scavenger.c`.

## Dependencies And Integration Points
The declarations require visible Samba types for talloc, messaging, tevent, and `files_struct` from the including compilation unit's normal smbd headers. The header is the narrow integration boundary between durable-open code and the scavenger implementation.

## Risks And Test Signals
Risks are minimal but include missing prototypes when callers do not include the right type definitions first and accidental broadening of the interface if internals are moved here. Test signals are compile coverage for smbd setup and durable disconnect call sites, plus runtime tests covered by `scavenger.c`.
