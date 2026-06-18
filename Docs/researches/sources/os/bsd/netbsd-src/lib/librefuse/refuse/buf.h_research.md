# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/buf.h

This header declares the FUSE buffer API added in FUSE 2.9. It defines buffer flags, copy flags, `struct fuse_buf`, `struct fuse_bufvec`, `FUSE_BUFVEC_INIT`, `fuse_buf_size`, and `fuse_buf_copy`.

The header explicitly notes NetBSD ignores splice-related flags because Linux `splice(2)` has no direct local equivalent. ABI sensitivity is around the public struct layouts and macro initializer compatibility.
