# sources/user-network-fs/nfs-ganesha/src/include/sal_data.h

## Purpose
This is the core State Abstraction Layer data model. It defines the in-memory structures for NFSv4/NFSv4.1 client IDs, sessions, stateids, owners, locks, delegations, layouts, recovery records, async state work, per-object state handles, and grace-period events.

## Important APIs, Types, And Control Flow
Major types include `nfs41_session_t` with fore/back channel attributes, slot tables, connection lists, callback state, refcount, and revoked-delegation flags; `state_t` with object/export/owner pointers, typed `union state_data`, stateid sequence/other fields, and refcount; owner structures for NFSv4, NLM, and 9P; `nfs_client_id_t` and `nfs_client_record_t`; `state_lock_entry_t`, `state_block_data_t`, and `state_cookie_entry_t`; `state_file`, `state_dir`, and `state_hdl`; layout segment/recall structures; async queue records; and `nfs_grace_start_t`. It also provides inline `free_state`, stateid compare/copy macros, `obj_is_junction`, and tracepoint macros.

## State And Persistence
This header declares extensive process-global state: pools, hash tables for sessions/state/client IDs/owners, recovery directories, blocked lock lists, debug lists, client-id pools, and delegation counters. Persistent behavior is indirect through recovery directories/backends, revoked delegation records, quota/lock state in FSALs, and client reclaim metadata; the structs themselves are in-memory lifetime anchors.

## Dependencies And Integration Points
It depends on atomic/memory/list/hashtable utilities, FSAL pNFS and object types, config parsing, LTTng trace helpers, NFS protocol data, and optional NLM/9P types. It is consumed by SAL implementation files, NFSv4 protocol operations, export/client managers, FSAL object handles, session transport handling, metrics, and server statistics.

## Risks And Test Signals
Concurrency and lifecycle are dominant risks: documented lock ordering is `STATELOCK` then owner `so_mutex` then state `state_mutex`; client record mutex must not be acquired under `cid_mutex`; references must balance across state, owner, client, session, lock, and object pointers. Tests should stress open/close/lock/delegation/session churn, client expiration and reclaim, layout recall, junction detection, blocked lock grants/cancels, recovery grace transitions, and sanitizer/thread-sanitizer coverage for refcount and lock-order bugs.
