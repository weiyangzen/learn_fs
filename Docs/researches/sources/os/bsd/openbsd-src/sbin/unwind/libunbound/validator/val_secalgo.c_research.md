# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_secalgo.c

This file provides the crypto-backend adapter for DNSSEC validation. It maps DNSSEC/NSEC3/DS algorithms to OpenSSL, NSS, or Nettle calls depending on compile-time configuration.

Shared validator-facing API:
- `nsec3_hash_algo_size_supported()` reports supported NSEC3 digest length.
- `secalgo_nsec3_hash()` hashes NSEC3 input, currently SHA-1.
- `secalgo_hash_sha256()` computes SHA-256.
- `secalgo_hash_create_sha384()`, `secalgo_hash_create_sha512()`, `secalgo_hash_update()`, `secalgo_hash_final()`, and `secalgo_hash_delete()` provide streaming hash support.
- `ds_digest_size_supported()` and `secalgo_ds_digest()` support DS digest calculation.
- `dnskey_algo_id_is_supported()` declares supported DNSKEY algorithms.
- `verify_canonrrset()` verifies canonicalized RRset bytes against a DNSKEY public key and RRSIG signature block.

OpenSSL path:
- Supports SHA-1, SHA-256, SHA-384, SHA-512, optional GOST, DSA, RSA, ECDSA, Ed25519, and Ed448 depending on macros.
- Converts DSA signatures to DER via `setup_dsa_sig()`.
- Converts raw ECDSA DNSSEC signatures to ASN.1 DER via `setup_ecdsa_sig()`.
- Builds EVP public keys in `setup_key_digest()`.
- Uses `EVP_DigestVerify*` or older `EVP_VerifyFinal` APIs.
- Handles OpenSSL 3 digest refusal as `sec_status_indeterminate` when detectable.

NSS path:
- Implements hash support through NSS `HASH_*` APIs.
- Builds NSS public key objects for RSA, DSA, and ECDSA.
- Adds ASN hash prefixes for RSA verification where needed.
- Uses `PK11_Verify()` and maps bad signatures to bogus, missing modules to unchecked.

Nettle path:
- Implements direct digest helpers for SHA-1/SHA-256/SHA-384/SHA-512.
- Parses and verifies DSA, RSA, ECDSA, and Ed25519 signatures with Nettle primitives.
- Performs explicit DNSSEC wire key parsing for RSA exponent/modulus and DSA parameters.
- Returns human-readable reason strings for signature and key parsing failures.

Security behavior:
- RSAMD5 is rejected as deprecated.
- SHA-1 and DSA can be faked for unit testing via `fake_sha1` and `fake_dsa`.
- Algorithm support is compile-time gated and may also depend on FIPS mode or runtime provider availability.
- Signature mismatch maps to bogus; allocation or crypto-library operational failures generally map to unchecked or indeterminate.

Research notes:
- This file does not canonicalize RRsets; it assumes `val_sigcrypt.c` already built the canonical verification buffer.
- The file’s complexity is mostly portability glue across three crypto stacks.
- OpenSSL, NSS, and Nettle all expose the same validator-facing function names, so only one backend block compiles.
