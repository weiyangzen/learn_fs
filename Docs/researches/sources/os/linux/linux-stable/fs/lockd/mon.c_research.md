# File Research: sources/os/linux/linux-stable/fs/lockd/mon.c

Implements the in-kernel Network Status Monitor client used by lockd to coordinate reboot notifications with local `rpc.statd`.

Main behavior:
- `nsm_create()` builds an RPC client to local loopback `rpc.statd` using NSM program 100024 version 1.
- `nsm_monitor()` sends `NSMPROC_MON` for a peer not already monitored and updates `nsm_local_state`.
- `nsm_unmonitor()` sends `NSMPROC_UNMON` when the last non-sticky reference is released.
- `nsm_get_handle()` looks up or creates per-netns NSM handles by hostname or address depending on `nsm_use_hostnames`.
- `nsm_reboot_lookup()` matches statd reboot callbacks by private cookie.
- `nsm_release()` drops and frees handles.

Handle details:
- Hostnames containing `/` are rejected.
- `nsm_init_private()` creates a private cookie from current time and handle address to avoid stale-cookie collision across reboots.
- Address text is cached in `sm_addrbuf`.

XDR:
- Encodes NSM strings, monitor identity, callback identity, and private data.
- Decodes monitor/unmonitor status and state.
- Defines RPC procedure table for MONITOR and UNMONITOR.

Synchronization:
- Per-net NSM handle lists are protected by `nsm_lock`.
