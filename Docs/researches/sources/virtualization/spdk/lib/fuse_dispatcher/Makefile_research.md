# File Research: sources/virtualization/spdk/lib/fuse_dispatcher/Makefile

Build recipe for SPDK `fuse_dispatcher` library.

Behavior:
- Sets `SPDK_ROOT_DIR` two directories up and includes `mk/spdk.common.mk`.
- Declares shared object version `3.0`.
- Builds `fuse_dispatcher.c` into library `fuse_dispatcher`.
- Adds SPDK include root to `CFLAGS`.
- Uses `fuse_dispatcher.map` as the symbol map.
- Includes `mk/spdk.lib.mk` for standard SPDK library build rules.
