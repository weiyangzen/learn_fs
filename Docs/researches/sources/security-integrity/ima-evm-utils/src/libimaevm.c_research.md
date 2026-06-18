
# sources/security-integrity/ima-evm-utils/src/libimaevm.c

## Purpose
`libimaevm.c` implements the reusable IMA/EVM cryptographic library. It calculates file hashes, loads public and private keys, derives key IDs, creates and verifies IMA/EVM signature formats v1/v2/v3, handles X.509 SKID extraction, supports PKCS#11 via OpenSSL engine/provider abstractions, and initializes OpenSSL algorithms.

## Important APIs, Types, And Functions
Hashing starts with `ima_calc_hash2()` and `add_file_hash()`. Public key APIs include `read_pub_pkey()`, `read_pub_key()`, `imaevm_init_public_keys()`, `imaevm_free_public_keys()`, and key lookup via `find_keyid()`. Signing APIs include `imaevm_signhash()`, `sign_hash_v2()`, optional `sign_hash_v1()`, and `imaevm_create_sigv3()`. Verification APIs include `imaevm_verify_hash()`, `ima_verify_signature2()`, `verify_hash_v2()`, `verify_hash_v3()`, and optional v1 verification. Key ID helpers are `calc_keyid_v1()`, `calc_keyid_v2()`, `read_keyid_from_cert()`, and `imaevm_read_keyid()`.

OpenSSL access is abstracted by `read_priv_pkey()`, `read_priv_pkey_engine()`, `read_priv_pkey_provider()`, and `check_ossl_access()`. On OpenSSL 3.5+, ML-DSA message signing and verification use `create_sigv3_mldsa()` and `verify_mldsa()`.

## Control Flow
Signing reads a private key, builds a signature header, selects the digest algorithm, derives or overrides the key ID, initializes an EVP signing context, signs either the supplied digest or a sigv3-derived `ima_file_id` digest, and returns the binary header plus signature. Sigv3 first binds xattr type, hash algorithm, and file hash into a compact `ima_file_id`; for ML-DSA it signs the message form directly.

Verification validates xattr type and signature version, extracts the hash algorithm and key ID, finds the public key, configures EVP verification, and validates either the raw file digest or the sigv3 derived digest. Public key initialization accepts comma/space/tab-separated certificate paths and builds a linked list of `public_key_entry` objects.

## State And Persistence
`imaevm_params` stores global defaults. `g_public_keys` supports deprecated global-key APIs. Signature buffers and key IDs are persistent ABI data written by callers into xattrs or keyrings. `find_keyid()` mutates the public-key list by appending placeholder entries for unknown key IDs, which affects repeated diagnostics.

## Dependencies And Integration Points
The library depends on OpenSSL EVP, X.509, PEM, provider/store/UI, optional engine APIs, Linux byte-order macros, and kernel-compatible hash names. It is the central integration point for `evmctl`, tests, and external libimaevm consumers.

## Risks
Cryptographic behavior depends heavily on OpenSSL version and compile-time options. PKCS#11 URIs require explicit nonzero key IDs. Sigv2 refuses key types that do not sign hashes, while sigv3 adds direct ML-DSA message signing under OpenSSL 3.5+. Buffer sizes are conservative for common RSA but sigv2 uses a 1024-byte internal payload limit, so large non-ML-DSA signatures can fail. Global params and deprecated globals are not naturally thread-safe.

## Test Signals
`sign_verify.test`, `ima_hash.test`, `gen-keys.sh`, and `softhsm_setup` exercise hash/sign/verify, X.509 SKID, PKCS#11, and algorithm variants. Kernel tests validate that portable and fs-verity signatures interoperate with live IMA appraisal.
