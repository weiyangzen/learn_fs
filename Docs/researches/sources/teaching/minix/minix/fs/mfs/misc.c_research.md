# File Research: sources/teaching/minix/minix/fs/mfs/misc.c

`misc.c` currently provides `fs_sync`, the service sync operation. It iterates over the in-core inode table and writes every dirty, referenced inode with `rw_inode(..., WRITING)`.

After inodes are written, it flushes all dirty libminixfs buffers with `lmfs_flushall`. The ordering is intentional: inode writes leave modified disk-inode blocks in the buffer cache, so data/cache blocks must be flushed last.
