# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_state.c

## Purpose

`nfs4x_state.c` owns NFSv4.1 server session state lifecycle. It defines session lookup indexes, creates and destroys sessions/channels, negotiates channel limits, manages fore-channel replay slots, removes sessions during client teardown, tracks delegation recall race metadata, and initializes the NFSv4.1 session state table.

## Main Interfaces

Session lookup and references:

- `rfs4x_session_rele`
- `rfs4x_session_hold`
- `rfs4x_findsession_by_id`
- `rfs4x_findsession_by_clid`
- `rfs4x_createsession`

Session destruction/removal:

- `rfs4x_destroysession`
- `rfs4x_client_session_remove`
- `rfs4x_destroy_session_channel`

Channel and slot helpers:

- `sess_chan_limits`
- `rfs41_create_session_channel`
- `rfs41_destroy_back_channel`
- `nfs4x_csa_flags_valid`

Recallable-state race helpers:

- `rfs41_deleg_rs_hold`
- `rfs41_deleg_rs_rele`

State table lifecycle:

- `rfs4x_state_init_locked`
- `rfs4x_state_fini`

Important private callbacks include `rfs4_session_create`, `rfs4_session_destroy`, and `rfs4_session_expiry`.

## Session Indexing

Sessions are indexed by `sessionid4` and secondarily by `clientid4`. The session id is an illumos-constructed union containing fixed padding, server start time, and a unique atomic session counter. The session-id hash uses the unique session index.

`rfs4x_findsession_by_id()` searches the primary session index. `rfs4x_findsession_by_clid()` searches the secondary clientid index. `rfs4x_createsession()` uses a unique key that cannot collide with existing clientid associations and lets the common NFSv4 DB layer invoke `rfs4_session_create()`.

## Channel Limit Negotiation

`sess_chan_limits()` clamps or validates negotiated channel attributes:

- Fore-channel max requests is capped by `rfs4_max_slots`.
- Back-channel max requests must be between 1 and `rfs4_back_max_slots`.
- Minimum request/response sizes are enforced for both fore and back channels.
- Fore-channel max operations is capped by `NFS4_COMPOUND_LIMIT`.
- Back-channel max operations must support at least two operations.
- Cached response size is capped to a small slot-cache payload plus SEQUENCE header size.
- Back-channel cached response size is forced to zero.

Unsupported persistent reply cache and RDMA create-session flags are cleared during session creation.

## Session Creation

`rfs4_session_create()` performs the actual session object initialization:

- Holds the parent client DB entry.
- Builds a session id from server start time and unique session counter.
- Validates CREATE_SESSION flags.
- Initializes callback security, defaulting to `AUTH_NONE` if the client supplies no callback security parameters.
- Initializes session access time, flags, callback program, credentials, and reply-cache count.
- Attempts bidirectional RPC callback setup when `CREATE_SESSION4_FLAG_CONN_BACK_CHAN` is requested.
- Creates the fore channel, and if bidirectional callback succeeds, uses it as both fore and back channel.
- Copies requested fore/back channel attributes and validates them with `sess_chan_limits()`.
- Inserts the session into the parent client's session list unless the client is being destroyed.
- Creates a backchannel slot table when bidirectional callback is active.
- Allocates fore-channel replay slots, each with its own mutex.

On failure it tears down allocated channels and releases the client reference.

## Session Destruction And Expiry

`rfs4x_destroysession()` rejects destruction with `NFS4ERR_DELAY` when DB references exceed the expected in-use count. If a backchannel exists, it calls `slot_cb_status()` to reject destruction while callback slots are busy. On success it invalidates the session DB entry and removes the session from the client list.

`rfs4x_client_session_remove()` forcibly invalidates and removes all sessions for a closing client without refcount checks.

`rfs4_session_destroy()` destroys backchannel slot tables, flushes callback channels, frees callback security state, frees cached replay slot replies, destroys fore/back channels, removes the session from the client list, and releases the parent client.

`rfs4_session_expiry()` expires invalid sessions or sessions whose parent client lease has expired.

## Slot Replay Cache

Fore-channel slots are allocated by `slots_alloc()` and freed by `slots_free()`. Each `rfs4_slot_t` has a mutex and may hold a cached `COMPOUND4res`. `slots_free()` destroys slot mutexes and frees cached replies for slots marked `RFS4_SLOT_CACHED`.

The slot replay-cache behavior is completed by `rfs4x_sequence_prep()` and `rfs4x_sequence_done()` in `nfs4x_srv.c`; this file supplies the storage and cleanup routines.

## Backchannel Channels

`rfs41_create_session_channel()` creates a generic session channel. For back or both directions it also allocates `sess_bcsd_t`, initializes its mutex, and attaches it as channel-specific data.

`rfs41_destroy_back_channel()` destroys the backchannel-specific data and the channel lock. `rfs4x_destroy_session_channel()` handles fore-only, back-only, both, and bidirectional-RPC cases, including the case where fore and back pointers refer to the same channel object.

## Recallable-State Race Tracking

`rfs41_deleg_rs_hold()` and `rfs41_deleg_rs_rele()` manage a reference count inside delegation recall-state tracking. When the count reaches zero, the stored session id, sequence id, and slot number are cleared. This supports the `rfs4x_rs_record()`/`rfs4x_rs_erase()` logic in `nfs4x_srv.c`.

## State Table Initialization

`rfs4x_state_init_locked()` creates the NFSv4.1 session table with the common NFSv4 DB framework, then creates:

- A primary unique session-id index.
- A non-unique clientid secondary index.

`rfs4x_state_fini()` is intentionally empty because the caller destroys the common state tables.

## Dependencies

This file depends on the common NFSv4 server DB/index framework, client records, lease timing, RPC service callback controls, slot-table support from `nfs4x_slrc.c`, and backchannel security helpers implemented in `nfs4x_srv.c`.

## Research Notes

This file is where negotiated protocol limits become concrete kernel allocations. Audit hotspots are channel size validation, backchannel slot-table allocation from client-provided limits, bidirectional channel pointer ownership, session/client list removal races, cached reply cleanup, and forced session invalidation during client teardown.
