# File Research: sources/virtualization/spdk/lib/idxd/Makefile

This Makefile builds the SPDK `idxd` library. It always compiles `idxd.c` and `idxd_user.c`, and conditionally adds `idxd_kernel.c` when `CONFIG_IDXD_KERNEL=y`.

It sets `SPDK_ROOT_DIR`, includes common SPDK make rules, declares shared-object version `14.0`, names the library `idxd`, uses `spdk_idxd.map` as the symbol map, and includes `spdk.lib.mk`.

Research notes: kernel IDXD support is build-time optional; the user-space PCI implementation is always part of the library.
