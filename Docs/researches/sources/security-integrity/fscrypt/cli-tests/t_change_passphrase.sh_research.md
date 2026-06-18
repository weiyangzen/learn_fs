# sources/security-integrity/fscrypt/cli-tests/t_change_passphrase.sh

## Purpose
End-to-end test for changing a custom passphrase protector.

## Control Flow and Integration
Creates an encrypted directory with passphrase `pass1`, verifies `pass2` cannot unlock, resolves the protector descriptor, changes passphrase non-interactively with old and new inputs, verifies old passphrase fails and new passphrase succeeds, tests interactive mismatch, then changes interactively to `pass3` and validates lock/unlock.

## State and Risks
Exercises `fscrypt metadata change-passphrase`, protector rewrapping, key wiping, and locked directory behavior. It relies on expect prompt strings and status of encrypted directories after lock.

## Test Signals
Covers both non-interactive and interactive passphrase change paths, including mismatch rejection.
