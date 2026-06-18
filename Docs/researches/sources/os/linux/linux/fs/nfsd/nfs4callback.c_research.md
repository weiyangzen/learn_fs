# File Research: sources/os/linux/linux/fs/nfsd/nfs4callback.c

This file implements the NFSD server-side NFSv4 callback/backchannel RPC client. It builds and tears down per-network-namespace callback RPC program metadata, encodes callback COMPOUND requests, decodes callback replies, manages NFSv4.1 callback slots and `CB_SEQUENCE`, and runs callback work items against each `nfs4_client`.

Primary responsibilities:
- Encode/decode callback XDR for `CB_NULL`, `CB_RECALL`, `CB_RECALL_ANY`, `CB_GETATTR`, `CB_LAYOUTRECALL` when pNFS is enabled, `CB_NOTIFY_LOCK`, and `CB_OFFLOAD`.
- Translate callback `nfsstat4` values to Linux negative errno-style task status.
- Build `CB_COMPOUND` headers and update operation counts after appending callback operations.
- For NFSv4.1+, prepend `CB_SEQUENCE`, validate session ID, slot ID, sequence number, and target highest slot in replies.
- Create RPC clients for NFSv4.0 callbacks and NFSv4.1 backchannel callbacks.
- Queue, requeue, probe, shut down, and destroy callback work.
- Maintain callback channel state: unknown, up, down, fault, kill/update flags, callback inflight count, and callback session slot ownership.

Important entry points and exports:
- `nfsd_net_cb_init()` / `nfsd_net_cb_shutdown()` allocate and release the per-netns callback RPC program, version table, proc table counts, and stats.
- `nfsd4_init_cb()` initializes an individual `struct nfsd4_callback` with its client, RPC procinfo, operation callbacks, work item, flags, status fields, held slot, and referring-call list.
- `nfsd4_run_cb()` increments callback inflight accounting and queues callback work on the client callback workqueue.
- `nfsd4_probe_callback()` and `nfsd4_probe_callback_sync()` mark callback state unknown, request callback parameter update, and run the null probe.
- `nfsd4_change_callback()` updates stored callback connection data under `cl_lock`.
- `nfsd4_shutdown_callback()` marks the client kill bit, queues callback shutdown processing, flushes the callback workqueue, and waits for inflight callbacks to finish.
- `nfsd41_cb_referring_call()` and `nfsd41_cb_destroy_referring_call_list()` manage NFSv4.1 referring-call metadata carried in `CB_SEQUENCE`.

Core control flow:
- `nfsd4_run_cb()` queues `cb_work`; `nfsd4_run_cb_work()` serializes execution on `cl_callback_wq`.
- Before sending a callback, `nfsd4_run_cb_work()` processes pending callback updates, recreating or destroying the RPC client as needed via `nfsd4_process_cb_update()` and `setup_callback_client()`.
- For NFSv4.1 callbacks, `nfsd4_cb_prepare()` reserves a backchannel slot using `nfsd41_cb_get_slot()` before starting the RPC.
- Decode functions process `CB_COMPOUND` reply, then `CB_SEQUENCE` reply, then operation-specific status/payload.
- `nfsd4_cb_done()` handles v4.0 connection signal requeue, v4.1 sequence completion, operation status propagation, operation-specific done callbacks, and callback channel down/fault marking.
- `nfsd4_cb_release()` either requeues or destroys the callback.
- `nfsd41_destroy_cb()` releases held callback slots, clears running flags, calls operation-specific release handlers, and decrements inflight accounting.

State and synchronization:
- The client callback workqueue is relied on to serialize callback client recreation and access to `cl_cb_client`.
- `cl_lock` protects callback connection updates and backchannel session/connection lookup.
- Session `se_lock` protects callback slot bitmap, highest slot, and callback sequence numbers.
- `cl_cb_inflight` is an atomic counter with wakeup support for shutdown waits.
- Callback flags include running, wake, requeue, client update, and client kill semantics.
- NFSv4.1 callback slots are acquired before RPC start and released after sequence completion or callback destruction.
- Referring-call lists are caller-serialized, dynamically allocated, and explicitly destroyed by callback users such as offload callbacks.

Dependencies and integration:
- Uses SUNRPC client APIs: `rpc_create`, `rpc_shutdown_client`, `rpc_call_async`, `rpc_restart_call_prepare`, `rpc_delay`, wait queues, and procinfo tables.
- Uses NFSD state objects from `state.h`, XDR helpers from `xdr4cb.h`, `xdr4.h`, and generated `nfs4xdr_gen.h`.
- Interacts with pNFS layout recall code through `CB_LAYOUTRECALL`.
- Interacts with server-side copy through `CB_OFFLOAD`.
- Uses tracepoints throughout for callback setup, queueing, sequence status, errors, and release.
- Uses credentials from either machine credentials for NFSv4.0 or session callback security uid/gid for NFSv4.1+.

Error handling and notable risks:
- XDR encoding assumes reservations succeed in many helper paths and uses `WARN_ON_ONCE` or direct dereference after `xdr_reserve_space`; this is typical kernel XDR style but makes size estimates important.
- Callback errors can mark the channel down or faulty; NFSv4.1 sequence ambiguity can force session recovery.
- Slot sequencing is delicate: bad sequence, bad slot, or misordered sequence can intentionally leak/retire a slot and requeue.
- Callback client recreation depends on serialized workqueue execution; external code must preserve that assumption.
- `setup_callback_client()` has different credential and transport paths for v4.0 and v4.1+, including GSS principal validation for v4.0.
- Shutdown must wait for both queued work and async RPC release paths; inflight accounting is central to avoiding teardown races.
