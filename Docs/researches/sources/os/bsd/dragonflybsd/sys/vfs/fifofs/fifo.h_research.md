# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/fifo.h

Declares the public FIFO vnode operation interface. It includes `sys/vnode.h`, exports `fifo_vnode_vops`, and declares `fifo_vnoperate` and `fifo_printinfo`.

`fifo_vnoperate` is the generic dispatcher used by filesystem-specific FIFO wrappers, such as ext2’s `ext2_fifoops`, to delegate default FIFO behavior. `fifo_printinfo` lets owning filesystems include FIFO reader/writer state in vnode print output.

Important dependencies: consumed by filesystems that support named pipes, including `ext2_vnops.c`, and implemented by `fifo_vnops.c`.

Notable risks or research hooks: no include guard is present in this header, so repeated inclusion depends on conventional usage.
