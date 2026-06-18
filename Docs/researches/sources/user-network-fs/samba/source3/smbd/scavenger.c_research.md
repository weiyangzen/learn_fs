# sources/user-network-fs/samba/source3/smbd/scavenger.c

## Purpose
This file implements the smbd scavenger helper process that cleans up disconnected durable opens after their timeout expires. Parent smbd processes schedule cleanup work by messaging a parent-owned scavenger controller, which starts or reuses a forked `smbd-scavenger` child and forwards cleanup messages to it.

## Important APIs, Types, And Functions
The exported functions are `smbd_scavenger_init` and `scavenger_schedule_disconnected`. Internal state lives in `smbd_scavenger_state` with tevent/messaging contexts, parent server id, optional scavenger server id, and an `am_scavenger` flag. `scavenger_message` contains `file_id`, `open_persistent_id`, and an absolute `NTTIME until`. Cleanup-specific helpers include `scavenger_add_timer`, `scavenger_timer`, `share_mode_cleanup_disconnected`, and `cleanup_disconnected_share_mode_entry_fn`.

## Control Flow
Initialization registers `MSG_SMB_SCAVENGER`. A disconnected durable open calls `scavenger_schedule_disconnected`, computes the timeout from disconnect time plus durable timeout, asserts the open is marked disconnected, and sends a `scavenger_message` to the original parent smbd. The parent-side message handler starts the scavenger if needed using `socketpair` and `fork`, waits for the child to send its `server_id`, then forwards the message. The child reinitializes smbd state after fork, sets process title and logging, watches the parent pipe for death, handles SIGTERM, receives only parent-origin messages, and schedules tevent timers. Timer expiry first calls `smbXsrv_open_cleanup`, then removes byte-range locks and share-mode entries for the disconnected persistent open, and removes stale leases if needed.

## State And Persistence
Persistent effects are cleanup of global open records, byte-range locks, share-mode entries, and lease records. Runtime state includes one global `smbd_scavenger_state`, a forked helper process, socketpair fd monitors used for parent/child liveness, messaging registrations, and tevent timers holding copied cleanup messages. The child exits cleanly if the parent pipe becomes readable/dead.

## Dependencies And Integration Points
The file depends on smbd globals, messaging, serverid, tevent, fork reinitialization, share mode locking, byte-range lock cleanup, leases DB cleanup, open-global cleanup, and process/logging utilities. It integrates with durable handle disconnect paths and the locking subsystem; its correctness depends on disconnected server ids and persistent open ids matching share-mode records.

## Risks And Test Signals
Risks include failing to start the child under fork/socketpair pressure, message loss if the parent dies, cleanup timers scheduled with corrupt or stale messages, races with durable reconnect before timeout, panics if a supposedly disconnected share-mode entry is owned by a live server, and partial cleanup when open-global cleanup succeeds but share-mode/BRL cleanup fails. Tests should cover init idempotency, child restart after death, parent death handling, schedule timing, durable reconnect-before-timeout behavior, cleanup of share modes, byte-range locks and leases, spurious sender messages ignored by the child, and fork/reinit failure paths.
