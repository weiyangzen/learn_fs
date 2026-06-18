# File Research: sources/virtualization/spdk/lib/lvol/Makefile

Builds SPDK's logical volume library.

Key contents:
- Sets `SPDK_ROOT_DIR` and includes `mk/spdk.common.mk`.
- Declares ABI version `SO_VER := 13` and `SO_MINOR := 0`.
- Builds `lvol.c` into `LIBNAME = lvol`.
- Uses `spdk_lvol.map` as the export map.
- Includes the standard `mk/spdk.lib.mk` library rules.

Filesystem/block relevance:
- This Makefile produces the logical-volume layer that maps blobstore-backed allocation and snapshot features into SPDK lvol APIs used by virtual block devices.
