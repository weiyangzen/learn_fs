# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ioctladmin.h

Administrative ioctl ABI for `/dev/cryptoadm`. It defines control payloads for cryptographic provider inventory, disabled-mechanism configuration, software module management, pool control, door registration, and FIPS 140 mode state.

Key elements:
- Defines `ADMIN_IOCTL_DEVICE` as `/dev/cryptoadm` and the `CRYPTOADMIN(x)` command-number namespace.
- List/info structs expose hardware provider entries, software provider names, per-device/per-software mechanism lists, and disabled mechanism lists.
- Software-management payloads support unloading a software provider and loading software configuration.
- `crypto_load_door_t` carries a door id for userland administration integration.
- `crypto_fips140_t` carries a FIPS operation and resulting status.
- FIPS operation enum supports status query, enable, and disable.
- FIPS status enum distinguishes unset, validating, shutdown, enabled, and disabled modes.
- Defines admin command numbers for version, lists, provider info, disabled config, software unload/config, pool create/wait/run, door loading, and FIPS status/set.

Dependencies:
- Uses public crypto common types such as `crypto_dev_list_entry_t` and `crypto_mech_name_t`.
- Includes a 32-bit compatibility structure for `crypto_get_soft_list_t`, the payload with embedded pointer/size fields.

Research notes:
- Like `ioctl.h`, this is ABI-sensitive and uses trailing one-element arrays for variable-length mechanism/provider lists.
- The FIPS mode enum models both requested mode and framework validation/shutdown states, so consumers should not treat it as a simple boolean.
