# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nsm.c

Purpose: manages local NSM/statd monitor and unmonitor RPCs for NLM clients.

Important APIs/types/functions: exports `nsm_connect`, `nsm_disconnect`, `nsm_monitor`, `nsm_unmonitor`, and `nsm_unmonitor_all`; internal helpers are `nsm_monitor_noretry` and `nsm_unmonitor_noretry`. Global state includes `nsm_mutex`, `nsm_clnt`, `nsm_auth`, `nsm_count`, and `nodename`.

Control flow: connection setup obtains local nodename and creates a TCP RPC client to localhost statd. Monitor/unmonitor functions lock host and global NSM mutexes, avoid duplicate operations via `ssc_monitored`, issue `SM_MON`/`SM_UNMON`, update monitor count and atomics, and retry once after failures. `nsm_unmonitor_all` sends `SM_UNMON_ALL` for the NLM callback identity.

State and persistence: persists process-local statd client/auth handles and monitor counts. It also updates per-NSM-client monitored flags. Actual monitoring state is persisted externally in statd.

Dependencies and integration points: depends on TI-RPC/statd XDR, `state_nsm_client_t`, atomic helpers, admin shutdown configuration, and NLM callback identity constants.

Risks and test signals: mutex ordering, retry behavior after statd restart, monitor count underflow, nodename lifetime, and shutdown unmonitor policy need coverage. Test statd unavailable, statd restart retry, double monitor/unmonitor, admin shutdown with `unmonitor_on_shutdown` false, and unmonitor-all cleanup.
