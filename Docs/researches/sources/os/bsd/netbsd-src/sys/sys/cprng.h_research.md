# File Research: sources/os/bsd/netbsd-src/sys/sys/cprng.h

Declares the kernel cryptographic pseudo-random number generator interface.

Key content:
- Includes NIST hash DRBG and fast CPRNG headers.
- `CPRNG_MAX_LEN` aliases `NIST_HASH_DRBG_MAX_REQUEST_BYTES`.
- Opaque `cprng_strong_t`.
- Initialization and lifecycle APIs: `cprng_init`, `cprng_strong_create`, `cprng_strong_destroy`.
- Random extraction: `cprng_strong`, `cprng_strong32`, `cprng_strong64`.
- Flags: `CPRNG_INIT_ANY`, `CPRNG_REKEY_ANY`, `CPRNG_USE_CV`, `CPRNG_HARD`.
- Global generators: `kern_cprng`, `user_cprng`.

Important behavior:
- Header guard deliberately remains `_CPRNG_H` for external compatibility.
- Intended for kernel entropy consumers at different IPL/thread constraints.
