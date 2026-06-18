# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_register.c

`o2cb` configfs registration and unregistration operations.

Registration validates the cluster, initializes the `o2cb` stack, creates the cluster if needed, sets heartbeat mode, removes registered nodes that disappeared or changed in config, and adds configured nodes with local-node marking based on hostname prefix matching. Unregistration refuses to proceed unless the named cluster is active and has no active heartbeat regions, then unregisters nodes and removes the cluster.

Signals are blocked during register/unregister to reduce partial live configuration changes.
