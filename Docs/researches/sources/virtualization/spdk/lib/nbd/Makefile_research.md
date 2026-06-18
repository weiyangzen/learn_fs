# File Research: sources/virtualization/spdk/lib/nbd/Makefile

Build definition for SPDK's NBD library.

Key contents:
- Sets `SPDK_ROOT_DIR` to `../..` and includes common SPDK make rules.
- Declares shared library version `SO_VER := 9`, `SO_MINOR := 0`.
- Builds `LIBNAME = nbd` from `nbd.c` and `nbd_rpc.c`.
- Uses `spdk_nbd.map` as the symbol map.
- Includes `mk/spdk.lib.mk`.

Research notes:
- This makefile only wires the NBD core and RPC layer into the SPDK library build.
- Scope relevance: build plumbing for exposing SPDK bdevs as kernel NBD devices.
