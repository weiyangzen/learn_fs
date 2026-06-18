# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4callback.c

Purpose: implements the NFSD server-side NFSv4 callback RPC client. It builds and sends backchannel callbacks to NFSv4 clients for delegation recall, callback getattr, layout recall, lock notification, copy offload completion, and recall-any pressure.

Key structures and state:
- `nfs4_cb_compound_hdr` tracks CB_COMPOUND encoding state: minor version, callback ident, op count pointer, and decoded status.
- Per-net callback program resources are owned by `struct nfsd_net_cb`, initialized by `nfsd_net_cb_init()` and released by `nfsd_net_cb_shutdown()`.
- Callback execution is carried by `struct nfsd4_callback`, tied to `struct nfs4_client`, an RPC message, optional operation callbacks, flags, held backchannel slot, and referring-call lists.
- NFSv4.1+ callback slot state lives in `nfsd4_session`: `se_cb_slot_avail`, `se_cb_highest_slot`, and `se_cb_seq_nr`.

Major logic:
- XDR helpers encode/decode callback primitives: stateids, filehandles, sessionids, bitmaps, empty arrays, attributes, CB_COMPOUND headers, and operation statuses.
- Callback operation encoders cover `CB_GETATTR`, `CB_RECALL`, `CB_RECALL_ANY`, optional `CB_LAYOUTRECALL`, `CB_NOTIFY_LOCK`, and `CB_OFFLOAD`.
- Callback decoders validate CB_COMPOUND, optional `CB_SEQUENCE`, and the expected callback op result, then map NFS status codes to Linux errno-style values with `nfs_cb_stat_to_errno()`.
- `encode_cb_sequence4args()` and `decode_cb_sequence4resok()` implement the NFSv4.1 backchannel sequencing contract, including session ID, sequence number, slot ID, and target highest slot updates.
- `nfsd4_cb_sequence_done()` decides whether to advance sequence numbers, retry, requeue, mark the backchannel faulty, or leak a bad slot after protocol synchronization errors.
- `setup_callback_client()` constructs the RPC client differently for v4.0 callback addresses versus v4.1+ backchannel transports and credentials.
- `nfsd4_process_cb_update()` serializes callback transport updates, shuts down stale clients, finds a backchannel connection, and creates a new callback RPC client.
- `nfsd4_run_cb_work()` is the workqueue entry point: refreshes callback channel state, prepares operation-specific data, and launches the asynchronous RPC call.

Concurrency and lifetime:
- Callback work is serialized by `cl_callback_wq`; comments explicitly rely on no two callback work items running concurrently for one client.
- Backchannel slots are protected by `ses->se_lock`; waiters sleep on `cl_cb_waitq`.
- In-flight callback accounting uses `cl_cb_inflight` and `wait_var_event()` so shutdown can wait for all callbacks to drain.
- Referring-call list entries are dynamically allocated and must be destroyed with `nfsd41_cb_destroy_referring_call_list()`.
- Callback release either requeues a callback or destroys it, releasing slots, waking waiters, invoking operation release hooks, and decrementing in-flight count.

Important dependencies:
- Uses SunRPC client APIs: `rpc_create`, `rpc_call_async`, `rpc_restart_call_prepare`, `rpc_sleep_on`, and `rpc_shutdown_client`.
- Integrates with NFSD state objects from `state.h`, per-net state from `netns.h`, callback XDR size definitions from `xdr4cb.h`, generated XDR helpers from `nfs4xdr_gen.h`, and tracing from `trace.h`.
- Optional pNFS callback support is gated by `CONFIG_NFSD_PNFS`.

Risk/edge cases:
- CB_SEQUENCE mismatches are treated as serious backchannel faults because the server cannot trust client slot state.
- RPC-level failure leaves `cb_seq_status` at sentinel value `1`, causing conservative recovery behavior.
- `max_cb_time()` assumes the NFSv4 lease is at most one hour and warns if that invariant changes.
- For NFSv4.1+ callbacks, missing backchannel transport or session rejects callback client setup.
