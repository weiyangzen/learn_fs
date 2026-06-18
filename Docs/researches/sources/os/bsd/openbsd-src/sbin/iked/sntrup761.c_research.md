# File Research: sources/os/bsd/openbsd-src/sbin/iked/sntrup761.c

This file is an amalgamated public-domain SUPERCOP reference implementation of the Streamlined NTRU Prime `sntrup761` KEM, generated from multiple upstream SUPERCOP files and adapted to OpenBSD’s `crypto_api.h` type/function names.

Public API:
- `crypto_kem_sntrup761_keypair(unsigned char *pk, unsigned char *sk)`
- `crypto_kem_sntrup761_enc(unsigned char *c, unsigned char *k, const unsigned char *pk)`
- `crypto_kem_sntrup761_dec(unsigned char *k, const unsigned char *c, const unsigned char *sk)`

Key responsibilities:
- Provides constant-time-ish sorting helpers for signed and unsigned 32-bit arrays used in short polynomial generation.
- Implements division/modulo helpers avoiding variable-time CPU division for secret-dependent `x`, with `m` assumed constant.
- Fixes parameters to `SIZE761` and `SNTRUP`, not LPR.
- Implements recursive `Encode`/`Decode` for polynomial coefficient packing.
- Implements mod-3 and mod-q arithmetic, reciprocal calculations, ring multiplication, rounding, short polynomial generation, SHA-512 prefixed hashes, and random sampling.
- Implements Streamlined NTRU Prime core operations:
  - `KeyGen` generates public polynomial and secret components.
  - `Encrypt` computes rounded ciphertext polynomial.
  - `Decrypt` recovers the short input polynomial and masks failures.
- Implements encoding/decoding for small, full Rq, and rounded polynomials.
- Implements KEM construction:
  - `KEM_KeyGen` appends public key, random fallback secret, and public-key hash cache into the secret key.
  - `Encap` samples inputs, encrypts, confirms, and derives session key.
  - `Decap` decrypts, re-encrypts for confirmation, conditionally substitutes fallback secret on mismatch, and derives the final key.

Important dependencies:
- `crypto_api.h` supplies fixed-width crypto types, `randombytes`, and `crypto_hash_sha512`.
- No filesystem or socket I/O occurs; all OS dependence is through randomness and hash primitives.

Security and correctness notes:
- The decapsulation path uses `Ciphertexts_diff_mask` and masked substitution to avoid directly branching on ciphertext validity for the recovered secret.
- Comments explicitly discuss timing assumptions around division and multiplication.
- Large variable-length stack arrays are used throughout, matching the reference style.
