# File Research: sources/virtualization/spdk/lib/thread/Makefile

This Makefile builds the SPDK `thread` shared library.

It sets `SPDK_ROOT_DIR`, includes common SPDK rules, declares shared object version `13.0`, compiles `thread.c` and `iobuf.c`, names the library `thread`, points `SPDK_MAP_FILE` at `spdk_thread.map`, and includes `spdk.lib.mk`.

The build unit therefore packages the SPDK cooperative thread/message/poller subsystem together with the shared iobuf pool facility. ABI/export control is delegated to the map file.
