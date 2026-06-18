# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_callback_simulator.c

## Purpose

This file implements a DBus-exposed callback simulator for NFS-Ganesha. It lets operators or tests list confirmed NFSv4.0 client IDs, list NFSv4.1 session IDs, test a callback backchannel, and issue a fake `CB_RECALL` against a selected client ID.

The simulator is diagnostic and test-oriented. It is inspired by an upcall simulator and does not implement production delegation policy; it manually constructs callback operations and dispatches them through the callback subsystem in `nfs_rpc_callback.c`.

## Important APIs, types, and functions

`nfs_rpc_cbsim_pkginit` registers the DBus path `CBSIM` with interface `org.ganesha.nfsd.cbsim`. `nfs_rpc_cbsim_pkgshutdown` is a no-op placeholder.

DBus methods are described by `cbsim_get_client_ids`, `cbsim_get_session_ids`, and `cbsim_fake_recall`. Their method functions are `nfs_rpc_cbsim_get_v40_client_ids`, `nfs_rpc_cbsim_get_session_ids`, and `nfs_rpc_cbsim_fake_recall`.

`nfs_rpc_cbsim_get_v40_client_ids` walks `ht_confirmed_client_id`, appends a timestamp, and returns an array of `uint64_t` client IDs. `nfs_rpc_cbsim_get_session_ids` walks `ht_session_id`, base64-encodes each `NFS4_SESSIONID_SIZE` session ID with `b64_ntop`, and returns an array of strings.

`cbsim_test_bchan` gets a confirmed client ID with `nfs_client_id_get_confirmed` and invokes `nfs_test_cb_chan`. `cbsim_fake_cbrecall` obtains the client, gets a callback channel, constructs a fake `CB_RECALL`, dispatches it with `nfs_rpc_call`, and uses `cbsim_completion_func` for logging.

`cbsim_free_compound` is marked unused. It shows how to free a constructed callback compound and specifically handles freeing `CB_RECALL` file-handle storage before `cb_compound_free`.

## Control flow

Initialization builds static DBus descriptors and registers the path. There is no dynamic simulator thread or background state; DBus method calls execute the relevant table scan or callback dispatch path.

For `get_client_ids`, the method initializes a DBus reply, appends the current timestamp with `gsh_dbus_append_timestamp`, opens an array container, and for each hash partition takes the partition write lock, walks the red-black tree, appends `cid_clientid`, and unlocks.

For `get_session_ids`, the flow is the same except it walks `ht_session_id`, base64-encodes `session_data->session_id`, and appends strings. The buffer is stack-allocated with `alloca(2 * NFS4_SESSIONID_SIZE)`.

For `fake_recall`, the DBus method defaults to client ID `9315` if no valid uint64 argument is supplied, then calls `cbsim_test_bchan` and `cbsim_fake_cbrecall` regardless of the test result. `cbsim_fake_cbrecall` validates the confirmed client record, verifies the channel, client handle, and auth handle, allocates an RPC call, initializes a v4.0 one-op callback compound tagged `brrring!!!`, fills a synthetic `CB_RECALL4args`, and calls `nfs_rpc_call`.

The completion function logs success or abort status and, for successful calls, logs the RPC result status. It does not free simulator-specific data because the active fake recall path intentionally leaves the fake file-handle string to the call cleanup path and comments that it leaks.

## State and persistence behavior

This file owns no persistent mutable state beyond static DBus descriptors. It reads global NFS client/session hash tables and can trigger callback-channel side effects through `nfs_test_cb_chan`, `nfs_rpc_get_chan`, and `nfs_rpc_call`.

The fake recall allocates a transient `rpc_call_t` and callback compound. On immediate dispatch failure it calls `free_rpc_call`; on async completion the callback subsystem releases the call. The fake file handle is allocated with `gsh_strdup`, and the in-source comment says it leaks, so repeated simulator use can create diagnostic-only memory growth.

DBus replies include a timestamp, so output is intentionally time-varying. There is no durable storage or configuration mutation.

## Dependencies and integration points

The simulator depends on DBus support (`gsh_dbus_*`), NFSv4 client and session hash tables, red-black tree/hash-table internals, SAL lookup functions, callback channel APIs, XDR NFSv4 callback structures, and Ganesha memory/logging helpers.

It integrates with the callback package as a consumer of `nfs_test_cb_chan`, `nfs_rpc_get_chan`, `alloc_rpc_call`, `cb_compound_init_v4`, `cb_compound_add_op`, and `nfs_rpc_call`. It is most useful when combined with a live server, active NFSv4 clients, and DBus administrative tooling.

## Risks and edge cases

The hash-table scans take write locks even though they only read entries, which can block concurrent client/session table operations more than necessary. The scans do not take per-client or per-session references, so they rely on partition locks preventing object removal during iteration.

The `get_session_ids` DBus descriptor declares the output array as `at` even though the method appends strings. That type-signature mismatch is a likely DBus API bug or stale descriptor.

`cbsim_fake_recall` is v4.0-oriented: it calls `nfs_rpc_get_chan` and constructs a callback compound with minor version 0 and a v4.0 callback identifier. It does not use `nfs_rpc_cb_single`, so it bypasses the v4.1 `CB_SEQUENCE` and slot-management path.

The fake recall uses a hard-coded default client ID and returns DBus success even if the test or recall fails internally. That is acceptable for a rough simulator but weak for automated diagnostics.

The synthetic `stateid.other` initializer uses escaped text that may not represent the intended raw bytes, and the fake file handle is a string rather than a real Ganesha file handle. The code itself notes a leak for the fake file-handle allocation.

## Test signals

Useful tests include DBus introspection/type validation, listing clients/sessions from controlled hash tables, base64 session ID formatting, error behavior for unknown client IDs, callback-channel test failures, fake recall dispatch success/failure, and memory accounting after repeated fake recalls.

Because this code is diagnostic, operational test signals are DBus method availability under `/org/ganesha/nfsd/CBSIM`, timestamp shape, array element types, logs from `cbsim_completion_func`, and no server crash when methods are called with missing, wrong-type, or stale client IDs.
