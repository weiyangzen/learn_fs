# File Research: sources/virtualization/spdk/lib/ioat/Makefile

This Makefile builds the SPDK `ioat` library from `ioat.c`.

It sets `SPDK_ROOT_DIR`, includes common SPDK make rules, declares shared-object version `9.0`, names the library `ioat`, uses `spdk_ioat.map` for symbol exports, and includes `spdk.lib.mk`.

Research notes: this library’s implementation surface in the group is `ioat.c` plus its private internal header.
