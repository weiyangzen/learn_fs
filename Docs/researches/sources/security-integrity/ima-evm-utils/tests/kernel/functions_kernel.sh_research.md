
# sources/security-integrity/ima-evm-utils/tests/kernel/functions_kernel.sh

## Purpose
`functions_kernel.sh` extends the shared test harness with helpers for live-kernel IMA policy loading, xattr extraction, private key discovery/conversion, and public key loading into kernel keyrings.

## Important APIs, Types, And Functions
`get_xattr()` reads a named xattr in hex or text form. `check_load_ima_rule()` validates a proposed policy rule with `ima_policy_check.awk`, signs a temporary policy file with `evmctl sign -o -a sha256 --imasig`, and writes it to `/sys/kernel/security/ima/policy`. `get_private_key()` finds or copies/converts a kernel signing key. `load_public_key()` converts a certificate to DER and adds it to a selected keyring with `keyctl padd asymmetric`.

## Control Flow
The script sets `PATH` to include source and test directories, sources `../functions.sh`, and exposes helper functions. Policy loading is conservative: invalid rules hard-fail; overlapping rules warn outside test environments but hard-fail inside `TST_ENV`; duplicate rules are treated as success.

## State And Persistence
It can add IMA policy rules, create temporary signed policy files, copy key material, and add asymmetric keys to kernel keyrings. These effects may persist for the boot/session.

## Dependencies And Integration Points
It depends on `getfattr`, `awk`, `evmctl`, `openssl`, `keyctl`, securityfs, and accessible kernel signing key/certificate paths or explicit `TST_KEY_PATH`/`TST_CERT_PATH`.

## Risks
Policy loading is irreversible for the running kernel and can affect later tests. Key discovery supports several host paths but skips when unavailable. The helper assumes policy files must be signed before loading.

## Test Signals
All kernel tests that need signed policy updates or appraisal key setup depend on this file.
