# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbtool.c

Command dispatcher for the newer `o2cb` utility.

It defines the command table for cluster, node, heartbeat, listing, registration, heartbeat start/stop, and status operations. It parses global options, chooses the config file, loads configuration, dispatches the selected command, prints per-command usage when requested, and stores the config only when the command marked it modified.

It also provides `o2cbtool_block_signals()` and `o2cbtool_init_cluster_stack()`, the latter enforcing that the active cluster stack is `o2cb`.
