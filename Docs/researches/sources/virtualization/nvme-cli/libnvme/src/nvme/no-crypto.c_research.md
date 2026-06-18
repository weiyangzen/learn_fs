# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/no-crypto.c

## Role

Build-time fallback implementation for libnvme crypto/key-management APIs when crypto support is disabled.

## Behavior

Every exported crypto, TLS key, DH-HMAC-CHAP, host ID, and host NQN helper is present so consumers can link successfully, but functionality is unavailable:

- Most integer-returning functions return `-ENOTSUP`.
- String-returning helpers return `NULL`.
- Key description and host identity generators/readers return `NULL`.

## Covered API Areas

- TLS key import/export, versioned and compatibility forms.
- Linux keyring read/lookup/update/revoke/scan helpers.
- TLS key identity generation and insertion helpers.
- DH-HMAC-CHAP key generation and raw secret creation.
- Host ID and Host NQN generation/read helpers.

## Dependencies

Includes `errno.h`, `nvme/linux.h`, and `compiler-attributes.h`. Public functions use `__libnvme_public`.

## Notes

This file intentionally contains no side effects and no partial implementation. Callers must treat `-ENOTSUP` or `NULL` as feature-disabled results.
