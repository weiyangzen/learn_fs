
# sources/security-integrity/ima-evm-utils/tests/softhsm_setup

## Purpose
`softhsm_setup` creates, queries, and tears down a temporary SoftHSM token for PKCS#11 signing tests.

## Important APIs, Types, And Functions
Commands are `setup`, `getkeyuri`, `getpubkey`, and `teardown`. Functions include `setup_softhsm()`, `teardown_softhsm()`, `_getkeyuri_softhsm()`, `getkeyuri_softhsm()`, `getpubkey_softhsm()`, `usage()`, and `main()`. It uses `softhsm2-util` and `p11tool` to initialize a token named `swtpm-test` and generate/export an RSA key.

## Control Flow
Startup checks for required tools and SoftHSM version. Setup creates or backs up SoftHSM config, initializes a token if needed, generates a private key with either modern `--generate-privkey=rsa` or older `--generate-rsa`, then prints a `keyuri:` line with PIN value. Teardown deletes the token, restores config backups, and removes token directories.

## State And Persistence
It writes `softhsm2.conf`, token storage under `SOFTHSM_SETUP_CONFIGDIR`, and on macOS may temporarily replace `/etc/gnutls/pkcs11.conf`. PINs default to `1234` but can be overridden.

## Dependencies And Integration Points
`functions.sh` calls it through `_softhsm_setup()` and `_softhsm_teardown()`. It depends on `p11tool`, `softhsm2-util`, optional sudo on macOS, and GnuTLS PKCS#11 configuration.

## Risks
Config backup/restore must be correct to avoid disturbing user SoftHSM/GnuTLS state. The printed URI includes a PIN value for test convenience. Setup is sensitive to output parsing from external tools.

## Test Signals
Successful `setup` prints `keyuri: ...`, enabling PKCS#11 key tests for engine/provider code paths.
