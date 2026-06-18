# File Research: sources/local-fs/ocfs2-tools/mkfs.ocfs2/check.c

Implements pre-format safety checks and cluster-information resolution for `mkfs.ocfs2`.

Key responsibilities:
- Determines active cluster stack information through o2cb.
- Reads existing on-disk cluster information if the target already has OCFS2 metadata.
- Merges user-provided, active-cluster, and on-disk cluster values.
- Rejects incompatible cluster configurations unless forced.
- Checks whether the device is mounted or busy.
- For existing OCFS2 volumes, tries to initialize DLM and lock the cluster before overwriting.

Important functions:
- `is_classic_stack()`
- `cluster_fill()`
- `ocfs2_fill_cluster_information()`
- `ocfs2_check_volume()`

Dependencies:
- `o2cb_init`, `o2cb_running_cluster_desc`, `o2cb_setup_stack`.
- `ocfs2_open`, `ocfs2_check_if_mounted`, `ocfs2_initialize_dlm`, `ocfs2_lock_down_cluster`.

Research notes:
- `--force` bypasses several safety gates but prints explicit warnings.
- Global heartbeat requires the classic `o2cb` stack and cluster information.
- Local mount skips cluster-information filling.
