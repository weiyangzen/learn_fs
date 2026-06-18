# File Research: sources/os/linux/linux/fs/lockd/host.c

Purpose: Manages shared client/server `nlm_host` cache, RPC client binding, NSM handle sharing, host garbage collection, reboot notification dispatch, and per-net shutdown.

Key functionality:
- Maintains separate hash tables for client and server hosts keyed by peer address.
- `nlmclnt_lookup_host()` finds or creates client peer handles by address/protocol/version.
- `nlmsvc_lookup_host()` finds or creates server-side client handles, including source address matching.
- `nlm_bind_host()` lazily creates RPC clients with lockd program/version/protocol settings.
- `nlm_rebind_host()` forces UDP portmapper rebinding after timeout.
- `nlm_host_rebooted()` maps NSM notify cookies to hosts and triggers server cleanup or client recovery.
- `nlm_shutdown_hosts_net()` expires hosts in a net namespace, shuts down RPC clients, frees resources, and runs GC.
- `nlm_gc_hosts()` mark-and-sweeps unused server hosts.

Dependencies and integration:
- Uses `nsm_get_handle()`, `nsm_unmonitor()`, `nsm_reboot_lookup()` from `mon.c`.
- Calls server resource functions (`nlmsvc_mark_resources()`, `nlmsvc_free_host_resources()`) outside this work item.
- Uses `lockd_net` namespace state from `netns.h`.

Concurrency and risk notes:
- Global host cache is protected by `nlm_host_mutex`; individual RPC binding uses `host->h_mutex`.
- Client hosts are destroyed immediately on final ref; server hosts are GC’d after expiry/resources clear.
- Reboot notification loops drop and reacquire the global mutex, using NSM state to avoid processing a host repeatedly.
