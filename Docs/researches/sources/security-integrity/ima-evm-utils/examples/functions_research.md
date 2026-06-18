# sources/security-integrity/ima-evm-utils/examples/functions

## Purpose
Shared shell library for generating IMA/EVM signing keys and local CA material with OpenSSL.

## Important APIs, Types, And Functions
- `SUPPORTED_ALGORITHMS` lists RSA, EC, and ML-DSA options.
- `get_ossl_keyalgo` maps user algorithms to OpenSSL `-newkey` parameters and enforces OpenSSL >= 3.5 for ML-DSA.
- `get_ossl_keyalgo_detail` returns EC curve pkey options.
- `ima_gen_signing_key` creates a CSR/key and signs it with a local CA.
- `ima_gen_localca` creates a local CA key/cert pair.
- `ima_gen_signing_key_selfsigned` creates a self-signed EVM/IMA key and public key.

## Control Flow
Wrapper scripts source this file, choose a default or user-provided key algorithm, then call one generator. The functions write temporary OpenSSL config files via heredocs and invoke `openssl req`, `openssl x509`, and public-key extraction commands.

## State And Persistence
Creates key, CSR, DER certificate, PEM certificate, serial, and generated config files in the examples directory because wrappers `cd` there before sourcing.

## Dependencies And Integration Points
Depends on OpenSSL CLI behavior, hostname/whoami for certificate subject fields, and local CA files for non-self-signed signing keys.

## Risks And Edge Cases
There is a likely typo in the self-signed public-key case pattern `primve256v1`, so `prime256v1` may miss the EC-specific extraction path. Generated private keys are unencrypted (`-nodes`) and should be handled as sensitive material.

## Test Signals
Signals are generated key/cert files and nonzero OpenSSL failures propagated to wrappers.
