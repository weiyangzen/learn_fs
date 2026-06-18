<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/all/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/unlink/all/runtest.sh

## Purpose
Tree-wide unlink test for keyutils versions supporting one-argument unlink-all behavior.

## Important APIs, Types, And Functions
Uses `keyutils_at_or_later_than`, `create_keyring`, `create_key`, `link_key`, `unlink_key`, `expect_unlink_count`, `list_keyring`, and `expect_keyring_rlist`.

## Control Flow
Creates one keyring and key, verifies normal unlink, then creates twenty subkeyrings all linking the same key. A one-argument `unlink_key $keyid` removes all links across the tree and reports the count.

## State And Persistence Behavior
Builds and then tears down a larger kernel keyring graph. The key's link count is the core state under test.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Skipped for keyutils older than 1.5. Link-count expectations are exact and would break if search scope or output wording changes.

## Test Signals
Signals are zero links removed when already detached, twenty-one links removed for the tree case, and absence from all keyrings afterward.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/all/runtest.sh -->
