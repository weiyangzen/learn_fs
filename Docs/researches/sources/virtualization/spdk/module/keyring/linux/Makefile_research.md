# File Research: sources/virtualization/spdk/module/keyring/linux/Makefile

Builds the Linux kernel keyring-backed module.

Key elements:
- Compiles `keyring.c` and `keyring_rpc.c`.
- Produces `keyring_linux`.
- Links `-lkeyutils`.
- Uses shared object version `3.0`.
- Uses blank SPDK map file.

Dependencies:
- Included only when keyutils support is configured.

Research notes:
- Provides integration with Linux session keyrings.
