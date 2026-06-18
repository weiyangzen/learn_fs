# File Research: sources/virtualization/spdk/module/keyring/file/Makefile

Builds the file-backed keyring module.

Key elements:
- Compiles `keyring.c` and `keyring_rpc.c`.
- Produces `keyring_file`.
- Uses shared object version `4.0`.
- Uses `spdk_keyring_file.map`.

Dependencies:
- Built via SPDK library make fragment.

Research notes:
- Provides persistent config JSON for file-backed keys.
