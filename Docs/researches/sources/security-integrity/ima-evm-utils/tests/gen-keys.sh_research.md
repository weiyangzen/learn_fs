
# sources/security-integrity/ima-evm-utils/tests/gen-keys.sh

## Purpose
`gen-keys.sh` generates test private keys, public keys, and DER certificates used by signing and verification tests.

## Important APIs, Types, And Functions
The script creates `test-ca.conf`, then generates RSA keys/certs including a custom SKID variant, EC keys for `prime256v1` and `secp384r1`, GOST EC-RDSA keys for several paramsets, optional SM2 keys using `/opt/openssl3/bin/openssl`, and optional ML-DSA keys if the local OpenSSL supports `mldsa44`.

## Control Flow
With `clean`, it removes generated configuration and key/cert/pub files. With `force` or stale/missing outputs, it regenerates material. The `log()` helper echoes and evaluates OpenSSL commands. Algorithm blocks are guarded by tool availability and output existence.

## State And Persistence
Generated files are left in the tests directory for reuse and removed only by explicit clean/distclean. For the RSA SKID case, the script appends PEM certificate text to the private key to test combined key/cert handling.

## Dependencies And Integration Points
It depends on OpenSSL command-line behavior and the local `../src` path. Test scripts consume the generated `.key`, `.cer`, and `.pub` files to cover libimaevm signing and verification across algorithms.

## Risks
Algorithm availability varies by OpenSSL version and provider/engine configuration, making some generated key sets optional. `eval` in `log()` assumes controlled command strings. Long-lived generated keys are test-only and should not be confused with production keys.

## Test Signals
The breadth of generated algorithms provides direct coverage for RSA, EC, GOST, SM2, SKID-derived key IDs, and post-quantum ML-DSA paths when supported.
