# File Research: sources/virtualization/spdk/lib/init/Makefile

This Makefile builds the SPDK `init` library from `json_config.c`, `subsystem.c`, `subsystem_rpc.c`, and `rpc.c`.

It sets `SPDK_ROOT_DIR`, includes common SPDK make rules, declares shared-object version `8.0`, names the library `init`, uses `spdk_init.map` for exports, and includes `spdk.lib.mk`.

Research notes: the library combines subsystem lifecycle, JSON config loading, and framework RPC server/control-plane helpers.
