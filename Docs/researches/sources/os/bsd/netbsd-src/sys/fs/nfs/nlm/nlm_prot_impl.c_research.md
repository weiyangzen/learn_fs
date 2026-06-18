# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_impl.c

Implements the kernel Network Lock Manager core for NetBSD's NFS lockd path. It owns global NLM initialization, syscall registration, server startup, RPC client creation, host/sysid tracking, NSM monitor/unmonitor integration, waiting client lock state, async server-side blocked lock state, and the concrete NLM operations used by the RPC stubs.

Important entry points include `sys_nlm_syscall()`, `nlm_server_main()`, `nlm_find_host_by_name()`, `nlm_find_host_by_addr()`, `nlm_host_monitor()`, `nlm_host_get_rpc()`, `nlm_register_wait_lock()`, `nlm_wait_lock()`, `nlm_cancel_wait()`, and the RPC-operation helpers `nlm_do_test()`, `nlm_do_lock()`, `nlm_do_cancel()`, `nlm_do_unlock()`, `nlm_do_granted()`, `nlm_do_granted_res()`, and `nlm_do_free_all()`.

The host model assigns local sysids, stores caller names and remote addresses, caches RPC handles briefly, publishes per-host sysctl counters, tracks NSM monitor state, and maintains pending/granted/finished async lock lists. Reboot notifications from NSM call `nlm_host_notify()`, which cancels pending async locks, clears local lock-manager state with `lf_clearremotesys()`, and can start client lock recovery when local client locks exist.

Lock operations translate NLM locks into `struct flock` and call `VOP_ADVLOCK()` or `VOP_ADVLOCKASYNC()`. Blocking server locks allocate `nlm_async_lock`, send `GRANTED_MSG` callbacks when granted, and wait for `GRANTED_RES` acceptance; rejected grants are unlocked locally. Client-side blocking waits are matched by file handle, pid, offset, and length when `nlm_do_granted()` receives a granted callback.

Key dependencies are kernel RPC/krpc, rpcbind/portmap, local NSM protocol XDR, NFS file handle and export APIs, vnode/VFS operations, `nfs_lock` hooks, taskqueue callbacks, sysctl, syscall registration, and lockf helpers. Operational risks center on cross-thread races between async lock callbacks, host reboot cleanup, RPC handle expiry, and module lifetime; the module explicitly refuses unload.
