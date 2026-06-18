# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/o2cb_ctl.py

Wrapper around `/etc/init.d/o2cb` and `o2cb_ctl` commands.

Key constants:
- `DEFAULT_CLUSTER_NAME = 'ocfs2'`
- `O2CB_INIT = '/etc/init.d/o2cb'`
- `O2CB_CTL = 'o2cb_ctl'`

Key classes:
- `CtlError`
- `O2CBProcess(Process)`
  - Converts string or tuple args into command form.
- `O2CBCtl`
  - Program `o2cb_ctl`, title `Cluster Control`.
- `O2CBInit`
  - Program `/etc/init.d/o2cb`, title `Cluster Stack`.

Key functions:
- Init wrappers:
  - `init_load`
  - `init_online`
  - `init_status`
- Query wrappers:
  - `query_clusters`
  - `query_nodes`
- Mutation:
  - `add_node(name, cluster_name, ip_address, ip_port, parent)`
- Higher-level parsers:
  - `get_active_cluster_name`
    - Queries clusters.
    - Prefers `ocfs2`.
    - Creates default cluster if none exists.
  - `get_cluster_nodes`
    - Parses colon-delimited node output from `o2cb_ctl -I -t node -o`.

Notable details:
- Some command paths pass raw strings to `Process`, which uses shell-like behavior through `popen2.Popen4`; tuple paths are safer.
- Output parsing silently skips malformed lines and comments.
