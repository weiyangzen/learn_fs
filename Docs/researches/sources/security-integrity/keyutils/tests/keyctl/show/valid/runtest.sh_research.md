<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/show/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/show/valid/runtest.sh

## Purpose
Valid `keyctl show` test for nested keyrings and optional explicit-root display.

## Important APIs, Types, And Functions
Uses `create_keyring`, direct `keyctl show`, version helpers, `wc`, `tail`, `cut`, and shell loops.

## Control Flow
Creates seven nested keyrings under `@s`, shows the whole session tree, optionally checks line count and key ID order, and for keyutils >=1.5.4 checks `keyctl show <keyring>` for each nested root.

## State And Persistence Behavior
Mutates session keyring topology with a chain of keyrings. It does not explicitly unlink them, relying on session cleanup after the test.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Output formatting checks are gated by RHEL/keyutils version. Key ID list comparison assumes traversal order matches creation chain.

## Test Signals
Signals are successful show, expected number of lines, matching key ID order, and decreasing subtree sizes for explicit roots.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/show/valid/runtest.sh -->
