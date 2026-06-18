# File Research: sources/virtualization/spdk/lib/keyring/Makefile

Builds SPDK's `keyring` library.

Key contents:
- Sets `SPDK_ROOT_DIR` and includes `mk/spdk.common.mk`.
- Declares shared-library ABI version `SO_VER := 4` and `SO_MINOR := 0`.
- Builds `keyring.c` and `keyring_rpc.c` into `LIBNAME = keyring`.
- Uses `spdk_keyring.map` as the library export map.
- Includes the standard `mk/spdk.lib.mk` library rules.

Filesystem/block relevance:
- The keyring library provides secret/key management used by storage modules such as crypto-capable bdevs, so this Makefile controls whether the keyring implementation and RPC surface are linked as an SPDK library.
