<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/unlink/bad-args/runtest.sh

## Purpose
Bad-argument and invalid-object test for `keyctl unlink`.

## Important APIs, Types, And Functions
Uses `unlink_key --fail`, `create_key`, `unlink_key --wait`, and `expect_error`.

## Control Flow
Checks invalid source and keyring IDs, creates a non-keyring user key and uses it as a keyring argument to get `ENOTDIR`, then destroys the key and checks both source and destination stale-ID failures.

## State And Persistence Behavior
Creates one temporary user key and removes it. It depends on kernel key lifetime and unlink wait behavior.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The non-keyring and stale-ID cases depend on exact errno mapping. Lazy destruction could otherwise make stale ID checks flaky.

## Test Signals
Signals are `EINVAL`, `ENOTDIR`, and `ENOKEY` from invalid unlink targets.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/bad-args/runtest.sh -->
