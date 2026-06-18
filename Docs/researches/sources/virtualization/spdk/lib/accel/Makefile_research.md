# File Research: sources/virtualization/spdk/lib/accel/Makefile

This makefile builds the SPDK `accel` library. It sets shared-library version values `SO_VER := 18`, `SO_MINOR := 0`, and `SO_SUFFIX := $(SO_VER).$(SO_MINOR)`, names the library `accel`, and compiles `accel.c`, `accel_rpc.c`, and `accel_sw.c`.

Optional system libraries are added based on configuration. `CONFIG_HAVE_LZ4=y` adds `-llz4`. `CONFIG_ISAL_CRYPTO=y` attempts to add ISA-L Crypto library search paths and `-lisal_crypto`.

The makefile sets `SPDK_MAP_FILE` to the local `spdk_accel.map`, so symbol exports are controlled by that version map, then includes the standard SPDK library build rules through `mk/spdk.lib.mk`.

Notable caveat: the `CONFIG_ISAL_CRYPTO` line appears malformed as read: `LOCAL_SYS_LIBS += -L$(ISAL_CRYPTO_DIR/.libs -L$(ISAL_CRYPTO_DIR)/lib64 -lisal_crypto`. The first variable reference lacks the normal `)` placement around `ISAL_CRYPTO_DIR`, so this line should be verified before relying on that configuration path.
