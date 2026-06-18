# File Research: sources/virtualization/spdk/module/keyring/linux/keyring_linux.h

Declares Linux keyring module options and accessors.

Key elements:
- `struct keyring_linux_opts` contains `enable`.
- Declares `keyring_linux_set_opts()` and `keyring_linux_get_opts()`.

Dependencies:
- Includes SPDK stdinc for `bool`.

Research notes:
- Used by Linux keyring implementation and startup RPC code.
