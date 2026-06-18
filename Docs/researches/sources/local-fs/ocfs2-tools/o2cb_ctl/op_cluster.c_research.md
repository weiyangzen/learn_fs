# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_cluster.c

`o2cb` cluster add/remove operations.

It validates cluster names as nonempty, at most `OCFS2_CLUSTER_NAME_LEN`, and alphanumeric only. `add-cluster` creates a new config cluster, while `remove-cluster` removes an existing cluster and marks the command modified so the dispatcher stores the config.
