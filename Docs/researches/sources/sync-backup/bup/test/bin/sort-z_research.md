## sources/sync-backup/bup/test/bin/sort-z

Purpose: test helper that runs a null-delimited sort portably.

Important control flow: if `uname -s` is NetBSD, it executes `sort -R 000 "$@"`; otherwise it executes `sort -z "$@"`.

State and dependencies: stateless shell wrapper depending on platform `sort` behavior. It integrates with tests needing NUL-delimited ordering.

Risks and tests: platform-specific flags may drift with system utilities. The script exits immediately on command failure due to `set -e`.
