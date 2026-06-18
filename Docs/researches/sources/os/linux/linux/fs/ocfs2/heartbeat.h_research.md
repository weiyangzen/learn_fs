# File Research: sources/os/linux/linux/fs/ocfs2/heartbeat.h

Header for OCFS2 heartbeat-facing helpers.

Exports:
- `ocfs2_init_node_maps()`
- `ocfs2_do_node_down()`
- `ocfs2_node_map_set_bit()`
- `ocfs2_node_map_clear_bit()`
- `ocfs2_node_map_test_bit()`

Role:
- Lets DLM/cluster setup register node-down handling and lets recovery/orphan code maintain node bitmaps through shared helpers.
