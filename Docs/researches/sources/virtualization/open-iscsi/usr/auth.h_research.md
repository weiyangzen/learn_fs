# File Research: sources/virtualization/open-iscsi/usr/auth.h

Defines the CHAP authentication API, limits, enums, and context structures used by `auth.c`.

Key constants:
- String/block/binary limits: 256-byte strings, 1024-byte string blocks, 1024-byte large binaries.
- CHAP response lengths: MD5 16, SHA1 20, SHA256 32, optional SHA3-256 32.
- `ACL_SIGNATURE` validates initialized auth contexts.

Important structures:
- `auth_key` tracks key presence, processing, and string pointer.
- `auth_key_block` stores one receive/send key block plus validation flags.
- `iscsi_acl` stores configuration, negotiated method/algorithm, state-machine phase, CHAP challenges, key blocks, and session handle.

The header exposes the full negotiation API and keeps enum ordering tied to lookup tables in `auth.c`, especially key names and debug status text.
