# File Research: sources/teaching/os161/kern/vfs/device.c

Implements vnode operations for VFS devices by adapting `struct device_ops` to the vnode interface. `dev_eachopen` rejects creation, truncation, exclusive create, and append flags before delegating to `DEVOP_EACHOPEN`. Reads and writes validate seek position with `dev_tryseek`, assert correct `uio_rw`, then call `DEVOP_IO`.

Block devices require block-aligned offsets within device bounds; character devices are treated as nonseekable by `dev_isseekable`, though `dev_tryseek` currently accepts positions. `dev_stat` synthesizes size, block size, type, permissions, link count, and device numbers. Lookup of an empty suffix returns the device itself; nonempty suffixes fail.

`dev_create_vnode` allocates and initializes a permanent device vnode. `dev_uncreate_vnode` is only for failure paths.
