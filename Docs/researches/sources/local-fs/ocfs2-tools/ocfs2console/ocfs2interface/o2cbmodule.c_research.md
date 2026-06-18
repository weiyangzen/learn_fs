# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/o2cbmodule.c

Python 2 C extension binding a subset of `libo2cb`.

Exposed module:
- `o2cb`

Exposed types:
- `o2cb.Cluster`
  - Read-only `name`
  - Property `nodes`
  - Method `add_node`
- `o2cb.Node`
  - Read-only `name`
  - Property `number`

Exposed functions:
- `list_clusters()`
- `get_hb_ctl_path()`

Exposed constants:
- `O2NM_API_VERSION`
- `O2NM_MAX_NODES`
- `O2NM_INVALID_NODE_NUM`
- `O2NM_MAX_NAME_LEN`

Key implementation details:
- Wraps libo2cb calls:
  - `o2cb_create_cluster`
  - `o2cb_list_clusters`
  - `o2cb_list_nodes`
  - `o2cb_get_node_num`
  - `o2cb_add_node`
  - `o2cb_get_hb_ctl_path`
- Creates `o2cb.error` exception from `RuntimeError`.
- Uses `initialize_o2cb_error_table()` and `error_message(ret)`.

Notable details:
- Heartbeat region functions are present but compiled out under `#if 0`.
- Python 2 C API only.
- `Cluster.__init__` creates the cluster as a side effect.
