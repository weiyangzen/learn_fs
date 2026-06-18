# File Research: sources/virtualization/spdk/module/keyring/linux/keyring.c

Implements a keyring backend over Linux kernel keyutils.

Key elements:
- Tracks enablement in `g_opts`.
- Finds keys with `request_key("user", name, NULL, KEY_SPEC_SESSION_KEYRING)`.
- Probes keys by adding SPDK keyring entries when Linux keys exist.
- Stores Linux key serial number in per-key context.
- Reads key material with `keyctl_read()`.
- Emits config JSON as `keyring_linux_set_options`.
- Initializes only when enabled; otherwise returns `-ENODEV`.
- Registers keyring module `linux`.

Dependencies:
- Linux keyutils, SPDK keyring, keyring module, logging, string, and util APIs.

Research notes:
- Removal is a no-op at the Linux keyutils level; SPDK removes the keyring registration.
