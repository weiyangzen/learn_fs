# File Research: sources/virtualization/nvme-cli/libnvme/test/psk.c

## Role

`psk.c` is a fixed-vector test for libnvme TLS PSK import/export and TLS key identity generation helpers.

## Behavior

The file defines known PSK byte arrays, lengths, versions, HMAC algorithm IDs, expected exported key strings, and expected identity strings.

It tests:

- `libnvme_export_tls_key()`.
- `libnvme_import_tls_key()`.
- `libnvme_export_tls_key_versioned()`.
- `libnvme_import_tls_key_versioned()`.
- `libnvme_generate_tls_key_identity()`.
- `libnvme_generate_tls_key_identity_compat()`.

The import tests validate parsed HMAC, length, and raw PSK bytes. Export and identity tests compare generated strings exactly. Identity generation treats `-ENOTSUP` as a permissible skip, likely for builds without required crypto support.

`test_rc` accumulates failures and controls process exit.

## Dependencies

- Public libnvme API.
- CCAN `array_size`.
- Optional crypto capability behind libnvme’s TLS identity functions.

## Filesystem/Storage Relevance

This supports NVMe/TCP secure connection setup by validating TLS PSK serialization and identity derivation.
