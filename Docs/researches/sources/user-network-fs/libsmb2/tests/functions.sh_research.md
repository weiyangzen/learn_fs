<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/functions.sh -->
# sources/user-network-fs/libsmb2/tests/functions.sh

Purpose: Small shared shell helper for libsmb2 test scripts.

Important APIs, types, and functions: Defines `failure()` to print `TEST FAILED` and exit with status 1.

Control flow: Scripts source this file and call `failure` after commands that should not fail, or after commands that unexpectedly succeed.

State and persistence behavior: No persistent state.

Dependencies and integration points: Integrated by all shell tests via `. ./functions.sh`.

Risks: Only provides a generic failure path; it does not preserve command output or line numbers, which can make failures harder to diagnose.

Test signals: Every shell test in this subset uses it as the failure signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/functions.sh -->
