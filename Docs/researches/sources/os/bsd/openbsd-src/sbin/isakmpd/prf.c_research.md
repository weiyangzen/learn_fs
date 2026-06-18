# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/prf.c

This file implements isakmpd’s pseudo-random function abstraction, currently as HMAC over an existing hash implementation.

Key APIs:
- `prf_alloc(enum prfs type, int subtype, unsigned char *shared, unsigned int sharedsize)`: allocates a `struct prf`, binds it to a hash subtype, initializes HMAC state with shared key material, stores reusable HMAC contexts, and installs function pointers.
- `prf_free(struct prf *)`: releases PRF contexts and wrapper.
- `prf_hash_init()`, `prf_hash_update()`, `prf_hash_final()`: adapter functions making the PRF look like the hash interface.

Behavior and integration:
- Only `PRF_HMAC` is supported.
- Uses `hash_get(subtype)` and the hash object’s `HMACInit`/`HMACFinal` functions.
- Saves both HMAC internal contexts so `Init` can reset the reusable hash object before each PRF operation.

Risk notes:
- `prf_free()` assumes a non-null, fully initialized PRF.
- The PRF context references the shared hash object and copies hash internals; correctness depends on the hash implementation’s context ownership model.
