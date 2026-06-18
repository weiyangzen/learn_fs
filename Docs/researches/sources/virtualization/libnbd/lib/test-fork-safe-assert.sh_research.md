# File Research: sources/virtualization/libnbd/lib/test-fork-safe-assert.sh

Shell test wrapper for the fork-safe assertion test binary.

Flow:
- Runs `./test-fork-safe-assert`, capturing stderr.
- Verifies exit status is signal-based abort.
- Accepts `ABRT` or `SIGABRT` naming from `kill -l`.
- Greps for exact assertion failure format containing `FALSE`.
- Ensures `TRUE` does not appear in stderr.

Research notes:
- Validates both behavior and diagnostic stringification of failed assertion expression.
