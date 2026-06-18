# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_ctl.c

Legacy control program for O2CB configuration and live configfs changes.

It parses single-letter operation flags, object/type selections, and attributes; validates attributes for clusters or nodes; loads/stores `/etc/ocfs2/cluster.conf`; prints cluster/node information; creates clusters/nodes; and changes cluster name or online state. Online cluster changes create configfs cluster and nodes, mark exactly one local node based on hostname prefix matching, and offline changes remove active nodes and cluster.

Important limitations: delete mode is not implemented, node changes are not supported, heartbeat type appears in the man page but this code only validates cluster/node attributes, and return values are raw negative errno-style values from `main()`.
