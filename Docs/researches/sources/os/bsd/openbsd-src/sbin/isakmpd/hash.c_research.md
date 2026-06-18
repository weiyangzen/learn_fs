# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/hash.c

Hash and HMAC abstraction over MD5, SHA1, SHA256, SHA384, and SHA512.

Key pieces:
- Static wrappers adapt OpenBSD hash APIs to common `Init`, `Update`, `Final` signatures using `union ANY_CTX`.
- Static `hashes[]` maps internal enum values to ISAKMP/Oakley IDs, digest sizes, block sizes, shared temporary contexts, and HMAC hooks.
- `hash_get()` returns a pointer to the matching static hash descriptor.
- `hmac_init()` implements RFC-style HMAC key normalization, ipad/opad setup, and initializes inner/outer contexts.
- `hmac_final()` completes inner digest, feeds it into the outer context, and emits the final HMAC.

Notable details:
- Uses static temporary contexts and digest buffer; callers must not assume independent concurrent `struct hash` instances from `hash_get()`.
- HMAC key material is scrubbed with `explicit_bzero()`.
- Long HMAC keys are first hashed into the local key buffer.
