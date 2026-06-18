# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_auth.h

Declares the authentication-method vtable used by phase-1 code.

`struct ike_auth` fields:
- Authentication method ID.
- `gen_skeyid(struct exchange *, size_t *)`.
- `decode_hash(struct message *)`.
- `encode_hash(struct message *)`.

Exports:
- `ike_auth_get(u_int16_t)`

The header forward-declares `struct exchange`; `struct message` is referenced in function pointers and supplied elsewhere by including users.
