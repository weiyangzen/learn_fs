# File Research: sources/teaching/minix/minix/fs/ptyfs/node.h

`node.h` declares PTYFS node-management types and functions. `node_t` is an unsigned integer index. `struct node_data` stores the metadata associated with an allocated PTY slave node: device number, mode, uid, gid, and ctime.

The public interface supports initializing the node table, setting/updating a node by index, clearing a node, retrieving node data by index, and retrieving the maximum node index bound used for validation and iteration.
