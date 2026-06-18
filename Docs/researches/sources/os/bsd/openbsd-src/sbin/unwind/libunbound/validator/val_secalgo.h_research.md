# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_secalgo.h

This header declares the validator’s cryptographic algorithm abstraction. It hides OpenSSL/NSS/Nettle details behind stable DNSSEC validation functions.

Declared capabilities:
- NSEC3 hash support and one-shot hashing.
- SHA-256 one-shot hashing.
- Streaming SHA-384 and SHA-512 hash contexts.
- DS digest support and digest size lookup.
- DNSKEY algorithm support checks.
- Canonical RRset signature verification through `verify_canonrrset()`.

Key data type:
- `struct secalgo_hash` is opaque to callers and implemented per backend in `val_secalgo.c`.

Important function contracts:
- `nsec3_hash_algo_size_supported()` returns 0 for unsupported NSEC3 hash algorithms.
- `secalgo_nsec3_hash()` and `secalgo_ds_digest()` return false on unsupported algorithms or backend failure.
- `dnskey_algo_id_is_supported()` is used before expensive verification attempts.
- `verify_canonrrset()` returns secure, bogus, unchecked, or indeterminate depending on signature result and backend failure mode.

Research notes:
- This is the narrow crypto boundary used by both NSEC3 hashing and RRSIG verification.
- The header intentionally works on raw buffers, leaving DNS wire parsing and canonicalization to other validator files.
