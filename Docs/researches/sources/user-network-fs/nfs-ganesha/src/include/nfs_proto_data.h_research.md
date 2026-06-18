# sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_data.h

## Purpose

`nfs_proto_data.h` defines the common protocol request/result unions, dispatch descriptor shape, request object, callback channel types, client credential representation, NFSv4 compound execution state, and helper for current object state management.

## Important APIs, Types, and Functions

`nfs_arg_t` and `nfs_res_t` union all NFSv3, NFSv4 compound, MOUNT, NLM, RQUOTA, extended RQUOTA, and NFSACL argument/result types. `nfs_function_desc_t` binds service/free/XDR decode/XDR encode names and dispatch behavior flags (`MAKES_WRITE`, `NEEDS_CRED`, `CAN_BE_DUP`, `SUPPORTS_GSS`, `MAKES_IO`). `nfs_request_t` embeds `svc_req`, lookahead, op context, args, result pointer, function descriptor, and duplicate-request queue linkage. Callback networking uses `rpc_call_channel_t`, netid/nc mappings, and `gsh_addr_t`. `compound_data` tracks current/saved FH/object/DS/stateid, export permissions, request, op arrays, credentials, NFSv4.1 slot/session/replay data, QoS flags, sequence/slot IDs, response sizing, and op-specific resume data. `set_current_entry` manages refcounts and DS release.

## Control Flow

Dispatcher decodes into `nfs_arg_t`, selects an `nfs_function_desc_t`, initializes request/op context, calls the protocol handler, stores `nfs_res_t`, and frees via descriptor free functions. NFSv4 compound processing walks op arrays while mutating `compound_data` current/saved state.

## State and Persistence Behavior

Per-request state is transient but contains references to persistent objects, exports, client IDs, sessions, slots, stateids, and cached compound results. Refcount correctness in `set_current_entry`/`set_saved_entry` controls object lifetime.

## Dependencies and Integration Points

It depends on FSAL API, RQUOTA, NFSv3/v4, NLM, NFSACL, SAL data, RPC channels, pNFS DS handles, QoS, and TIRPC netid mappings. This is a central include for dispatch, duplicate request cache, callbacks, and protocol handlers.

## Risks and Test Signals

Risks include union misuse/free omissions, dispatch flag mismatches, stale object refs, saved/current DS lifetime mistakes, NFSv4.1 replay slot cache leaks, response-size accounting errors, and credential lifetime bugs. Tests should exercise each protocol descriptor, compound current/saved FH transitions, refcounting under failure, session replay, async resume data, response-size limits, and duplicate request integration.
