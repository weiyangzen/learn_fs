# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/prf.h

This header defines the PRF abstraction.

Key declarations:
- `enum prfs`: currently only `PRF_HMAC`.
- `struct prf`: PRF type, opaque context, output block size, and `Init`/`Update`/`Final` function pointers.
- `struct prf_hash_ctx`: hash pointer plus saved HMAC contexts.
- Public allocation/free functions: `prf_alloc()` and `prf_free()`.

Integration:
- Used by IKE key derivation paths that need a hash-like PRF interface independent of the selected hash subtype.
