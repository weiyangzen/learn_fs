# File Research: sources/virtualization/spdk/lib/notify/Makefile

Build definition for SPDK's notify library.

Key contents:
- Sets `SPDK_ROOT_DIR` to `../..` and includes common SPDK make rules.
- Declares shared library version `SO_VER := 8`, `SO_MINOR := 0`.
- Builds `LIBNAME = notify` from `notify.c` and `notify_rpc.c`.
- Uses `spdk_notify.map` as the symbol map.
- Includes `mk/spdk.lib.mk`.

Research notes:
- Simple build glue for the in-process notification registry and RPC query interface.
