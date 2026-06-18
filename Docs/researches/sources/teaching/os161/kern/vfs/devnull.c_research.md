# File Research: sources/teaching/os161/kern/vfs/devnull.c

Implements the `null:` device. `nullopen` accepts all opens. `nullio` returns immediate EOF for reads by doing nothing, and discards writes by setting `uio_resid` to zero without reading the source buffer. This intentionally allows writes from invalid pointers to succeed, matching traditional null-device behavior. `nullioctl` rejects all ioctls with `EINVAL`.

`devnull_create` allocates a `struct device`, fills its ops, marks it as a character device with zero blocks and block size one, clears private data, and registers it with `vfs_adddev("null", dev, 0)`.

Failure to allocate or register panics during bootstrap.
