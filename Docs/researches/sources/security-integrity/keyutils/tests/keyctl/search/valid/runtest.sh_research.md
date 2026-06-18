<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/search/valid/runtest.sh

## Purpose
Comprehensive valid-search behavior test for keyrings, duplicate descriptions, nested keyrings, permissions, linking, revocation, and attach-on-search.

## Important APIs, Types, And Functions
Uses `create_keyring`, `create_key`, `search_for_key --expect/--fail`, `link_key`, `unlink_key`, `set_key_perm`, `revoke_key`, `print_key`, and `expect_error`.

## Control Flow
Builds two keyrings, creates overlapping `user:lizard` keys, searches from session and direct keyrings, attaches search results to another keyring, links/unlinks keyrings to change traversal, manipulates search permissions, and finally revokes a key to check search failure semantics.

## State And Persistence Behavior
Exercises persistent kernel keyring topology: links between keyrings, duplicate keys by type/description, permission masks, and revoked key state. The script cleans up by unlinking the main keyring from `@s`.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Search behavior around revoked keys differs on old kernels and RHEL7 backports, so expected errno is gated. Permission masks are hard-coded and can be sensitive to key permission ABI changes.

## Test Signals
Signals include selected key ID precedence, attach-to-destination notification, keyring traversal visibility, permission-driven `EACCES`/`ENOKEY`, and post-revoke `EKEYREVOKED` or legacy `ENOKEY`.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/valid/runtest.sh -->
