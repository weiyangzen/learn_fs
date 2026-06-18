# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/nodeconfig.py

GUI for O2CB cluster node configuration and stack activation.

Key constants:
- Default cluster name: `ocfs2`
- Default node port: `7777`
- Port range: `1000` to `65534`

Key class:
- `ClusterConfig(Dialog)`
  - Shows existing nodes in a `gtk.TreeView`.
  - Allows adding/editing/removing new, unapplied nodes.
  - Existing active nodes are displayed but not editable.
  - Validates:
    - max node count via `o2cb.O2NM_MAX_NODES`
    - non-empty node name
    - max name length via `o2cb.O2NM_MAX_NAME_LEN`
    - IPv4 address via `IPEditor`
    - duplicate names/IPs
  - Applies new nodes through `o2cb_ctl.add_node`.
  - Reloads cluster state after apply.

Key function:
- `node_config(parent=None)`
  - Queries O2CB init status.
  - Attempts to load/start cluster stack if not loaded/mounted.
  - Gets or creates active cluster name.
  - Shows `ClusterConfig`.
  - After dialog, ensures selected cluster is online.

Dependencies:
- `ocfs2`, `o2cb` C extensions
- `o2cb_ctl`
- `IPEditor`
- `guiutil.Dialog`, `error_box`

Notable issues:
- `load_cluster_state()` catches `o2cb_ctl.CtlError` but raises `ConfError`, while the defined exception is `ConfigError`; this typo would raise `NameError` on that path.
- `edit_node()` updates row values but does not call `can_apply(True)`, so edited unapplied nodes may not enable Apply unless another change already did.
