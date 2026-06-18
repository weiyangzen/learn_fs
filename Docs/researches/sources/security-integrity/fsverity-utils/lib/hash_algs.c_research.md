# sources/security-integrity/fsverity-utils/lib/hash_algs.c

Purpose: This file defines supported fs-verity hash algorithms and OpenSSL-backed hash context operations.

Important APIs and functions: It maintains algorithm descriptors for SHA-256 and SHA-512, provides context creation, init/update/final/full-hash helpers, frees hash contexts, and exports lookup helpers by algorithm number or name plus digest-size queries.

Control flow and state: Hash contexts hold per-operation crypto state and refer to immutable algorithm descriptors. Lookup scans the supported algorithm table and returns zero/null for unknown algorithms.

Dependencies and integration points: Used by digest computation, signing validation, CLI hash-alg parsing, and tests. Depends on OpenSSL-compatible EVP APIs and common type definitions.

Risks and test signals: Risks include OpenSSL API compatibility, digest-size mismatch with UAPI constants, and accepting aliases inconsistently. Signals include test vectors, hash lookup tests, SHA-256/SHA-512 digest size assertions, and builds against supported crypto libraries.
