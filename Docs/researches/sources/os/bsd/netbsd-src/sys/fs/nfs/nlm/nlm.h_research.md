# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm.h

This header declares the kernel-facing Network Lock Manager interface used by NetBSD's imported NFS/NLM implementation. It covers host tracking, RPC client lookup, NSM monitoring, blocking-lock wait registration, server-side NLM operation implementations, recovery hooks, and the VOP advisory-lock bridge.

Key contents:
- Declares malloc type `M_NLM` when available.
- Defines `NLM_SYSID_CLIENT`, an offset added to host system IDs when recording NFS client locks in the local lock manager.
- Declares `struct nlm_host`, `struct vnode`, `nlm_zero_tv`, and global NSM state `nlm_nsm_state`.
- Declares netobj helper functions `nlm_make_netobj()` and `nlm_copy_netobj()`.
- Declares host lookup/reference APIs by caller name or address, host monitor registration, host release, RPC client retrieval, host sysid lookup, and remote NSM state lookup.
- Declares blocking lock wait-list APIs: register, deregister, wait with timeout/signal behavior, and cancel waits by vnode.
- Declares NSM notification handling and server-side NLM operation helpers: test, lock, cancel, unlock, granted, granted-result, free-all, and client recovery.
- Declares VFS-facing entry points `nlm_advlock()` and `nlm_reclaim()`.
- Declares `nlm_acquire_next_sysid()` for remote locks outside normal NLM handling.

Important behavior:
- `nlm_register_wait_lock()` must be called before sending a blocking lock RPC, because a granted callback can arrive at any time.
- `nlm_wait_lock()` removes the wait-list entry on timeout or signal; signal callers must send cancellation to the server.
- Host lookup returns a referenced host object; callers must release it.

Research notes:
- This file is the public contract between NFS client vnode code, NLM server code, host/NSM management, and advisory-lock implementation.
- Concurrency-sensitive areas are host reference lifetime, wait-list ordering, granted callback races, and forced-unmount cancellation.
