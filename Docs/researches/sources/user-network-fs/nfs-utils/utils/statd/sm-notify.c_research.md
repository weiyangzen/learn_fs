## sources/user-network-fs/nfs-utils/utils/statd/sm-notify.c

Purpose: Sends `SM_NOTIFY` RPCs to peers recorded in NSM state after local reboot/startup, with retry scheduling and optional lockd grace-period lift.

Important APIs/types/functions: `struct nsm_host`, `smn_lookup`, `smn_verify_my_name`, `smn_alloc_host`, `smn_create_socket`, `notify`, `notify_host`, `recv_reply`, `recv_rpcbind_reply`, `recv_notify_reply`, `insert_host`, `find_host`, and `record_pid`.

Control flow: `main` reads config/options, prevents duplicate default runs via `/run/sm-notify.pid`, verifies source name/address, retires monitored hosts into notify list, obtains NSM state, optionally daemonizes, creates a nonblocking reserved UDP socket, drops privileges, and enters `notify`. The loop sends due hosts in batches, first rpcbind lookup if needed, then SM_NOTIFY, backs off exponentially, rotates addresses after repeated retries, and removes hosts after successful qualified and unqualified notifications.

State and persistence: Reads and mutates NSM monitor/notify records through `support/nsm`; updates kernel NSM state; writes pid file; may write `Y` to `/proc/fs/lockd/nlm_end_grace`.

Dependencies and integration: Uses resolver APIs, nfs-utils config/logging, low-level RPC encode/decode from `nfsrpc`, and lockd grace-period integration.

Risks and test signals: DNS failures, stale rpcbind ports, IPv6 dual-stack behavior, pid-file semantics, and retry timeout caps are important. Tests should use fake NSM records, mocked rpcbind/notify replies, multiple addrinfo records, `--no-update-state`, source bind options, duplicate run detection, and grace-period file absence/presence.
