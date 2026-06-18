# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_config.c

Typed O2CB cluster configuration model and serializer.

It loads `/etc/ocfs2/cluster.conf`-style JConfig data into `O2CBConfig`, `O2CBCluster`, `O2CBNode`, and `O2CBHeartbeat` objects; validates required node fields, numeric ranges, IPv4 addresses, and heartbeat modes; and stores the model back through a temporary file plus `rename()` under `/etc/ocfs2`.

The model supports multiple clusters, cluster heartbeat mode, heartbeat regions, node add/delete/lookup by name or number, and node setters/getters. Defaults include local heartbeat mode and node numbers assigned from current cluster count unless overridden. A bug-risk area is that removing nodes decrements `c_num_nodes`, but explicit node numbers may be sparse, so node count is not necessarily a max-number-derived value.
