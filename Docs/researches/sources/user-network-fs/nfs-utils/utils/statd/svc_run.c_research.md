## sources/user-network-fs/nfs-utils/utils/statd/svc_run.c

Purpose: Custom RPC service loop for statd that multiplexes RPC listener fds with the local notification reply socket and timeout queue.

Important APIs/types/functions: Global `notify`, static `svc_stop`, `my_svc_exit`, and `my_svc_run`.

Control flow: The loop processes due notification entries, builds the RPC fd set, adds the notify socket, selects with a timeout based on the next notification, handles transient errors, processes notify replies first, then dispatches RPC requests via `svc_getreqset`.

State and persistence: Manages in-memory stop flag and global pending notify list only.

Dependencies and integration: Called from `statd.c`; uses `process_notify_list` and `process_reply` from `rmtcall.c`, plus SunRPC `svc_fdset`.

Risks and test signals: Timeout calculations depend on a valid `now`, and fd-set size is constrained by `FD_SETSIZE`. Tests should cover empty queue blocking, due queue processing, reply socket events, RPC-only events, EINTR handling, and `my_svc_exit`.
