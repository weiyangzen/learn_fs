
# sources/security-integrity/ima-evm-utils/src/imaevm.h

## Purpose
`imaevm.h` is the public and internal contract for libimaevm and `evmctl`. It defines IMA/EVM xattr types, signature formats, digest/key algorithm identifiers, metadata hash layouts, global library parameters, OpenSSL access wrappers, and the exported signing, verification, hash, key-loading, key-id, and signature-v3 APIs.

## Important APIs, Types, And Functions
Important constants include `DEFAULT_HASH_ALGO`, `DATA_SIZE`, `MAX_DIGEST_SIZE`, `MAX_SIGNATURE_SIZE`, `MAX_TEMPLATE_SIZE`, `NUM_PCRS`, and `DEFAULT_PCR`. `enum evm_ima_xattr_type` maps xattr payload types such as IMA digest, EVM HMAC, IMA/EVM digital signatures, portable signatures, and fs-verity signatures. `struct h_misc`, `h_misc_32`, and `h_misc_64` encode EVM metadata hash trailers.

Signature structures include deprecated `struct signature_hdr` for v1 and `struct signature_v2_hdr` for v2/v3 asymmetric signatures. `struct libimaevm_params` holds process-wide defaults. `struct imaevm_ossl_access` abstracts OpenSSL engine/provider handles. Exported modern APIs include `ima_calc_hash2()`, `imaevm_signhash()`, `imaevm_verify_hash()`, `ima_verify_signature2()`, `imaevm_init_public_keys()`, `imaevm_free_public_keys()`, `imaevm_hash_algo_from_sig()`, `imaevm_hash_algo_by_id()`, `calc_hash_sigv3()`, and `imaevm_create_sigv3()`.

## Control Flow
The header does not execute control flow, but it shapes caller behavior. Callers choose xattr type, hash algorithm, key files, signature flags, and OpenSSL access mode, then call library routines that fill or validate binary signature buffers matching these packed structs.

## State And Persistence
`imaevm_params` is a global mutable configuration object shared by the library and CLI. Its fields can alter default hash algorithm, key file, password, key ID, X.509 behavior, engine, and HMAC key path. The packed structs define persistent on-disk/in-xattr ABI and must remain kernel-compatible.

## Dependencies And Integration Points
The header depends on Linux `fs.h`, syslog, OpenSSL RSA/provider/engine types, and kernel hash enum compatibility through `hash_info.h` consumers. It is consumed by both CLI code and external libimaevm users, with deprecated wrappers kept for ABI/API continuity.

## Risks
Packed ABI changes would break existing xattrs and kernel interoperability. `MAX_SIGNATURE_SIZE` is sized for ML-DSA-87 and affects template limits; callers must still pass adequate buffers. Global mutable parameters are convenient but make thread safety and concurrent independent signing contexts risky. Deprecated v1 interfaces remain available under compatibility macros but should be avoided.

## Test Signals
Coverage is indirect through signing, verification, hash, and measurement tests. `gen-keys.sh` exercises RSA, EC, GOST, SM2, and ML-DSA paths when available; kernel tests validate signatures that the kernel must accept.
