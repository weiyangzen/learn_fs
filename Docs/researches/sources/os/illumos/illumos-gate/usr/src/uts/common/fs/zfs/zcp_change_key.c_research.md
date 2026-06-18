# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zcp_change_key.c

## Role
Supports the ZFS Channel Program `change_key` synctask by validating raw/hex wrapping keys, constructing `dsl_crypto_params_t`, and forwarding check/sync work to the SPA keystore change-key implementation.

## Main Logic
- `hexval()` converts a single hexadecimal digit to a nibble and panics if called with invalid input.
- `hex_to_raw()` validates exact buffer-sized hex input, checks every pair with `isxdigit()`, and decodes into raw bytes.
- `zcp_synctask_change_key_create_params()` accepts only `ZFS_KEYFORMAT_RAW` and `ZFS_KEYFORMAT_HEX`, copies/decodes into a fixed `WRAPPING_KEY_LEN` buffer, builds public and hidden nvlists, calls `dsl_crypto_params_create_nvlist(DCP_CMD_NEW_KEY, ...)`, frees nvlists, and zeroes the stack key buffer.
- `zcp_synctask_change_key_cleanup()` frees crypto params from a `spa_keystore_change_key_args_t`.
- `zcp_synctask_change_key_check()` delegates to `spa_keystore_change_key_check()` after format validation.
- `zcp_synctask_change_key_sync()` delegates to `spa_keystore_change_key_sync()`.

## Important Details
- Passphrase/PBKDF2 keys are deliberately unsupported because the kernel channel-program path has no PBKDF2 conversion support.
- RAW key length is checked before `bcopy()` to prevent overflowing `rawkey`.
- HEX keys must decode exactly to `WRAPPING_KEY_LEN`.
- Sensitive key material is cleared with `bzero()` before return.
