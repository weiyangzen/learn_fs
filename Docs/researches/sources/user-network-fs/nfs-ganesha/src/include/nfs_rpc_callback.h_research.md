# sources/user-network-fs/nfs-ganesha/src/include/nfs_rpc_callback.h

## Purpose

`nfs_rpc_callback.h` declares the NFSv4 callback RPC dispatch API for v4.0 callback channels and v4.1 backchannel/session callbacks.

## Important APIs, Types, and Functions

`nfs4_cb_tag_t` models callback tags. `cb_compound_init_v4`, `cb_compound_add_op`, and `cb_compound_free` build callback compound requests. `nfs_cb_call_states` tracks dispatch/finished/aborted call states. Allocation helpers create/free `rpc_call_t`, callback argop/resop arrays, and channel down flags on `nfs_client_id_t`. Channel and call APIs include `nfs_rpc_get_chan`, package init/shutdown, optional GSS status, `nfs_rpc_create_chan_v40`, `nfs_rpc_create_chan_v41`, `nfs_rpc_call`, `nfs_rpc_cb_single`, `nfs41_release_single`, and `nfs_test_cb_chan`.

## Control Flow

State/delegation/session code builds callback compounds, obtains or creates a callback channel, submits an RPC call with optional completion hook, and updates channel-down state or releases v4.1 single-call resources after completion.

## State and Persistence Behavior

Callback channels are live process state tied to client IDs or sessions, with CLIENT/AUTH/GSS objects declared in `nfs_proto_data.h`. Channel-down flags affect future callback attempts and delegation behavior.

## Dependencies and Integration Points

It depends on config, logging, NFS core, NFSv4 generated callback types, client ID/session state, GSS, and RPC channel destruction. It integrates with delegations, recalls, layouts, session backchannels, and callback simulator builds.

## Risks and Test Signals

Risks include callback compound allocation leaks, channel lifetime races with client/session destruction, stale channel-down state, GSS enable mismatch, and completion hook use-after-free. Tests should create v4.0 and v4.1 channels, send/test callbacks, simulate client channel failure/recovery, verify completion callbacks and resource release, and run delegation recall flows under reconnect.
