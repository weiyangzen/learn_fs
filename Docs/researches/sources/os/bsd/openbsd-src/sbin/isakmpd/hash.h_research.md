# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/hash.h

Declares hash algorithm constants, enum IDs, `struct hash`, HMAC pad constants, and hash lookup/init prototypes.

`struct hash` contains:
- Internal enum and ISAKMP/Oakley ID.
- Digest size and block length.
- Pointers to primary and secondary contexts.
- Shared digest pointer.
- Context size.
- Function pointers for normal hash and HMAC operations.

Supported algorithms:
- MD5, SHA1, SHA2-256, SHA2-384, SHA2-512.

Public API:
- `hash_get(enum hashes)`
- `hmac_init(struct hash *, unsigned char *, unsigned int)`
