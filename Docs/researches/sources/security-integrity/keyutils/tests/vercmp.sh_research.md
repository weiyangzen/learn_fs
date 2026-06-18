<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/vercmp.sh -->
# sources/security-integrity/keyutils/tests/vercmp.sh

## Purpose
Command-line tester for the shell version-comparison functions.

## Important APIs, Types, And Functions
Sources `version.inc.sh` and calls `version_less_than` with two user-supplied version strings.

## Control Flow
Validates that two parameters were supplied, compares them, and prints either `<` or `>=`.

## State And Persistence Behavior
No persistent state is changed. It only reads the sourced functions and writes stdout/stderr.

## Dependencies And Integration Points
Used as a small manual/debug harness for `version.inc.sh`, not by normal runtest scripts.

## Risks And Edge Cases
It inherits all parser limitations from `version_less_than` and only reports a boolean less-than relationship.

## Test Signals
Signals are exit code 2 for missing parameters and human-readable comparison output.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/vercmp.sh -->
