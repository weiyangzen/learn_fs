# File Research: sources/teaching/minix/minix/fs/ptyfs/node.c

`node.c` manages PTY slave node allocation metadata for PTYFS. The implementation preallocates a bitmap and `struct node_data` array sized by `NR_PTYS`, relying on the current system-global PTY limit.

`init_nodes` clears the allocation bitmap. `set_node` validates the requested index, sets the bitmap bit, copies the caller's device/mode/owner/time metadata into `node_data`, and allows updating an already allocated node. `clear_node` unsets the bitmap bit and intentionally ignores attempts to clear an unallocated node.

`get_node` returns `NULL` for out-of-range or unallocated indexes, otherwise returns the stored metadata pointer. `get_max_node` returns `NR_PTYS`; the comment notes that this is acceptable because the limit is small, even though a future implementation could track the actual highest allocated node.
