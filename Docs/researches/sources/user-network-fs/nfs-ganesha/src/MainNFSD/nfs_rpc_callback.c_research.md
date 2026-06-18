# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_rpc_callback.c

## Purpose

This file implements NFSv4 callback/backchannel RPC client management. It creates callback channels for NFSv4.0 clients from SETCLIENTID callback addresses, creates NFSv4.1 backchannel clients on established sessions/transports, dispatches `CB_COMPOUND` calls asynchronously, tests callback reachability with `CB_NULL`, manages v4.1 callback slots, and handles callback authentication.

The public API serves delegation/layout recall and other NFSv4 callback users through `nfs_rpc_cb_single`, while startup/shutdown code uses `nfs_rpc_cb_pkginit` and `nfs_rpc_cb_pkgshutdown`. GSS callback support is compiled under `_HAVE_GSSAPI`.

## Important APIs, types, and functions

Public functions include `nfs_rpc_cb_pkginit`, `nfs_rpc_cb_pkgshutdown`, `nfs_rpc_cb_set_gss_status` when GSS is enabled, `nfs_set_client_location`, `nfs_rpc_create_chan_v40`, `nfs_rpc_create_chan_v41`, `nfs_rpc_get_chan`, `nfs_rpc_destroy_chan`, `alloc_rpc_call`, `free_rpc_call`, `nfs_rpc_call`, `nfs41_release_single`, `nfs_test_cb_chan`, and `nfs_rpc_cb_single`.

`netid_nc_table` and `nfs_netid_to_nc` translate NFS network IDs such as `tcp`, `tcp6`, `udp`, `udp6`, `rdma`, and `rdma6` to internal `nc_type` values. `setup_client_saddr` parses NFSv4.0 universal address strings into `sockaddr_t` storage in `clientid->cid_cb.v40.cb_addr`.

NFSv4.0 channel creation uses `nfs_clid_connected_socket`, `clnt_vc_ncreatef` for TCP, `clnt_dg_ncreatef` for UDP, and authentication setup from the client credential. Supported auth flavors are `RPCSEC_GSS`, `AUTH_SYS`, and `AUTH_NONE`; GSS setup uses `nfs_rpc_callback_setup_gss`.

NFSv4.1 channel creation uses `nfs_rpc_create_chan_v41`. It locks `session->cb_chan.chan_mtx`, destroys an existing channel if it belongs to a different transport, creates an RPC client from the service transport with `clnt_vc_ncreate_svc` or `clnt_rdma_ncreatef`, selects `AUTH_NONE` or `AUTH_SYS` from `callback_sec_parms4`, and sets `session_bc_up`.

RPC call lifecycle is represented by `rpc_call_t`/`struct _rpc_call` and `struct clnt_req`. `alloc_rpc_call` increments `nfs_health_.enqueued_reqs`; `nfs_rpc_call` fills the request for `CB_COMPOUND`; `nfs_rpc_call_process` handles auth refresh retry, marks the call finished, invokes the completion hook, and releases the call; `nfs_rpc_call_free` frees the enclosing `rpc_call_t` and increments `dequeued_reqs`.

NFSv4.1 callback construction uses `construct_v41`, `release_v41`, `find_cb_slot`, and `release_cb_slot`. Every v4.1 single-op callback is wrapped in a two-op compound with `CB_SEQUENCE` followed by the requested callback operation.

## Control flow

Package initialization sets up the GSS credential cache machinery and validates mechanisms when GSS is compiled in. Package shutdown clears and destroys GSS callback resources.

For NFSv4.0, `nfs_set_client_location` records the client's callback netid and address. `nfs_rpc_create_chan_v40` validates the auth flavor, opens and connects a socket to that address, creates a libntirpc client, attaches an auth handle, and leaves the channel in `clientid->cid_cb.v40.cb_chan`. `nfs_rpc_v40_single` refuses calls if the callback channel is marked down, obtains or creates a channel, constructs a one-op `CB_COMPOUND`, and dispatches it with `nfs_rpc_call`.

For NFSv4.1, session setup calls `nfs_rpc_create_chan_v41` when a backchannel is negotiated. Later, `nfs_rpc_get_chan` scans the client's v4.1 session list under `cid_mutex` and returns the first session whose `session_bc_up` flag is set. `nfs_rpc_v41_single` walks those sessions, reserves a callback slot, gets a stable session reference, drops `cid_mutex`, constructs the call with `CB_SEQUENCE`, dispatches it, and returns success if dispatch started. On dispatch failure it clears `session_bc_up`, releases the slot without advancing the sequence, drops the session reference, and retries with another session; after one full pass it retries once with a short slot wait.

`nfs_rpc_call` serializes access to the channel with `chan_mtx`, fills the client request with XDR functions for `CB_COMPOUND4args` and `CB_COMPOUND4res`, configures asynchronous completion, and calls `CLNT_CALL_BACK`. If setup or dispatch fails, it destroys the channel and marks the call aborted. Successful async completion flows later through `nfs_rpc_call_process`.

`nfs_test_cb_chan` ensures a channel exists, verifies client and auth handles, sends `CB_NULL` with `rpc_cb_null`, and retries once if the result is `RPC_INTR`. A failed null call destroys the channel so the next attempt can recreate it.

## State and persistence behavior

The file persists callback channel state inside `nfs_client_id_t` for v4.0 and `nfs41_session_t` for v4.1. Channels contain a libntirpc client handle, auth handle, type, source pointer, GSS security parameters, `chan_mtx`, and `last_called`. Destroying a channel tears down auth and client handles and resets `last_called`.

V4.1 backchannel state includes `session_bc_up`, `cb_mutex`, `cb_cond`, `bc_slots[]`, slot sequence numbers, and session references. `find_cb_slot` increments the sequence when reserving a slot; `release_cb_slot(..., sent=false)` rolls it back if the call was never sent. Completion hooks must call `nfs41_release_single` for v4.1 calls to release the slot and session reference.

GSS callback enablement is global process state protected by `gss_callback_status.lock`. Disabling GSS clears the credential cache; enabling GSS initializes the callback credential directory and refreshes machine credentials.

`alloc_rpc_call`/`nfs_rpc_call_free` update health counters, and request allocation is tied to libntirpc completion. `free_rpc_call` frees callback arg/result arrays and releases the `clnt_req`; final object memory is freed by the request free callback.

## Dependencies and integration points

The file depends on libntirpc client APIs (`clnt_vc_ncreatef`, `clnt_dg_ncreatef`, `clnt_vc_ncreate_svc`, `CLNT_CALL_BACK`, `CLNT_CALL_WAIT`, `clnt_req_*`), NFSv4 XDR structures, SAL client/session data, GSS credential cache helpers, pthread locks/condition variables, socket APIs, and Ganesha memory/logging helpers.

It integrates with NFSv4 client ID setup (`nfs_set_client_location`), session creation, delegation/layout recall users via `nfs_rpc_cb_single`, callback simulator code, state referral tracking through `struct state_refer`, and server health counters.

## Risks and edge cases

NFSv4.0 universal-address parsing is fragile by nature: `setup_client_saddr` splits on the last two dots to extract port bytes, then passes the remaining string to `inet_pton`. Malformed addresses silently leave zeroed socket state except for warnings, and unsupported netids later fail channel creation.

V4.0 UDP channel creation sets `raddr.maxlen/len` to `sizeof(struct sockaddr_in6)` regardless of actual address family, while TCP uses `sizeof(struct sockaddr_in)`. This should be validated because IPv6 TCP and IPv4 UDP sizes can be mismatched.

GSS callback support only formats host principals for `RPC_CHAN_V40`; v4.1 RPCSEC_GSS callback security parameters are explicitly skipped. Deployments requiring v4.1 GSS callbacks will fail to select that auth path.

The async call ownership contract is easy to violate. V4.1 callers must provide a completion callback and eventually call `nfs41_release_single`; the code calls `LogFatal` if no completion hook is provided because slot/session leaks would otherwise occur. V4.0 calls do not have the same slot-release requirement.

`nfs_rpc_get_chan` returns a v4.1 channel pointer after releasing `cid_mutex`; correctness depends on session/channel lifetime being protected by subsequent call code obtaining a session reference in `nfs_rpc_v41_single`. Direct external use of the returned pointer would be riskier.

Channel failure policy is coarse: most failed calls destroy the channel or clear `session_bc_up`. This avoids repeated use of broken paths but can amplify transient errors into callback unavailability until reestablishment.

## Test signals

Test signals should cover address parsing for IPv4/IPv6 universal addresses, unsupported netids, TCP/UDP v4.0 channel creation, auth flavor selection, GSS enable/disable behavior, failed and successful `CB_NULL`, v4.1 channel replacement when a new transport is supplied, RDMA compiled/uncompiled behavior, and security parameter fallback order.

V4.1 tests should verify slot reservation, highest-slot calculation, sequence rollback on unsent failure, release on completion, retry with short wait, session reference balancing, and clearing `session_bc_up` on dispatch errors. Async call tests should verify completion hook invocation, auth-refresh retry, health counter balance, channel destruction on failure, and no leaks of `CB_SEQUENCE` referral allocations.
