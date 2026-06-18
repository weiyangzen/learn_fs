<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/revoke/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/revoke/valid/runtest.sh

## Purpose
Functional revoke test for a user key and a keyring. It confirms that revoked objects remain referenced but reject describe, read, list, and further validation operations with `EKEYREVOKED`.

## Important APIs, Types, And Functions
Uses `create_keyring`, `create_key`, `list_keyring`, `describe_key`, `print_key`, `revoke_key`, and `unlink_key`, plus `expect_keyring_rlist`, `expect_key_rdesc`, `expect_payload`, and `expect_error`.

## Control Flow
Creates a session-attached keyring, adds a `user` key, verifies listing, description, and payload, revokes the key, checks revoked-key failures, unlinks it, then revokes and validates failures on the keyring itself.

## State And Persistence Behavior
Mutates the kernel session keyring by adding one keyring and one key, then revoking and unlinking them. The revoked state is durable within key lifetime; log state is persisted in `$OUTPUTFILE`.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The test assumes revocation returns `EKEYREVOKED` consistently for reads/describes/lists. Cleanup depends on unlinking revoked objects still being allowed.

## Test Signals
Signals include successful pre-revoke visibility, `EKEYREVOKED` after key revoke, and `EKEYREVOKED` after keyring revoke.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/revoke/valid/runtest.sh -->
