# File Research: sources/os/linux/linux/fs/lockd/mon.c

Purpose: Kernel client for the Network Status Monitor service (`rpc.statd`), including peer monitor/unmonitor upcalls, NSM handle caching, reboot notification matching, and NSM XDR.

Key functionality:
- Creates loopback TCP RPC clients to `rpc.statd` program 100024 version 1.
- `nsm_monitor()` sends MON requests and records local NSM state.
- `nsm_unmonitor()` sends UNMON when the last non-sticky reference is released.
- Caches `nsm_handle` objects per net namespace by hostname or address depending on `nsm_use_hostnames`.
- Rejects hostnames containing `/`.
- Generates private cookies from timestamp and handle address to match later notify callbacks.
- `nsm_reboot_lookup()` matches incoming reboot private data to cached handles.
- Encodes NSM MON/UNMON arguments and decodes monitor/stat results.

Dependencies and integration:
- Used by `host.c` for host allocation, destruction, and reboot processing.
- Uses `lockd_net.nsm_handles`.
- Uses SUNRPC client and XDR stream APIs.

Risk notes:
- NSM upcalls are local loopback RPCs but still subject to statd availability and connection refusal.
- The private cookie is designed to be unique across runtime and reboots, but stale/corrupt user-space notifications are still ignored only by cache mismatch.
- `nsm_use_hostnames` changes cache matching behavior, affecting handle reuse and monitor identity.
