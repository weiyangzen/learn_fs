# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_status.c

`o2cb cluster-status` implementation.

It initializes the stack, gets the currently active cluster from configfs, optionally compares it to the requested cluster name, checks whether the cluster is registered, and reports online if local heartbeat is configured or if global heartbeat has at least one active region. It returns `0` for online and `1` for offline.
