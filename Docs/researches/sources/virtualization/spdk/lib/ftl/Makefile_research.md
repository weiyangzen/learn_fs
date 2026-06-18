# File Research: sources/virtualization/spdk/lib/ftl/Makefile

## Purpose
Build definition for SPDK `ftl` library.

## Key Build Settings
- Sets `SPDK_ROOT_DIR`, includes `mk/spdk.common.mk`, and declares `LIBNAME = ftl`.
- Shared object version is `SO_VER := 11`, `SO_MINOR := 0`.
- Optional compile defines:
  - `SPDK_FTL_RETRY_ON_ERROR`
  - `SPDK_FTL_L2P_FLAT`
  - `SPDK_FTL_ZONE_EMU_BLOCKS=<value>`
- Adds `-I.` to local includes.

## Source Coverage
Builds core FTL files, management files, utilities, upgrade handlers, NV-cache implementations, and base-device implementations. Includes `ftl_trace.c` only for `CONFIG_DEBUG=y`.

## Clean Behavior
Adds manual clean targets for `mngt`, `utils`, and `upgrade` subdirectories before including `mk/spdk.lib.mk`.
