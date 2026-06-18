# File Research: sources/virtualization/spdk/module/bdev/crypto/Makefile

This makefile builds the `bdev_crypto` module from `vbdev_crypto.c` and `vbdev_crypto_rpc.c`. It sets shared-library version `8.0`, includes `$(ENV_CFLAGS)`, uses SPDK's blank map file, and delegates to `mk/spdk.lib.mk`.

The parent bdev makefile includes this directory only when `CONFIG_CRYPTO` is enabled, matching the module's dependency on SPDK accel crypto support.
