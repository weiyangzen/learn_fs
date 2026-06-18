# File Research: sources/virtualization/spdk/module/keyring/Makefile

Top-level build dispatcher for keyring backends.

Key elements:
- Always builds `file`.
- Builds `linux` when `CONFIG_HAVE_KEYUTILS` is enabled.
- Uses SPDK subdir build infrastructure.

Dependencies:
- Backend build files live under `module/keyring/file` and `module/keyring/linux`.

Research notes:
- Separates generic event keyring subsystem from concrete key storage providers.
