# sources/security-integrity/ecryptfs-utils/scripts/current-version.sh

Purpose: defines a shell environment variable for the current eCryptfs kernel version used by legacy scripts.

Important APIs/data: exports `ECRYPTFS_VERSION="2.6.20-rc2-mm1"`.

Control flow/state: sourced by other scripts; no standalone behavior.

Dependencies/integration: used by `rebuild-patches.sh`, `sync-kernel.sh`, and `test.sh`.

Risks: hard-coded old kernel version must be updated manually; `test.sh` supplies a fallback only if empty.

Test signals: scripts echo/use the expected version.
