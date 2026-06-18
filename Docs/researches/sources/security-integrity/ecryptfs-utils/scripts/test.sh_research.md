# sources/security-integrity/ecryptfs-utils/scripts/test.sh

Purpose: prints the configured eCryptfs kernel version for legacy scripts.

Important APIs/commands: sources `./current-version.sh`, falls back to `2.6.18-rc4-mm2` if `ECRYPTFS_VERSION` is empty, then echoes it.

Control flow/state: read-only except environment variable assignment in the shell process.

Dependencies/integration: smoke helper for current-version behavior.

Risks: uses bash-style `==` under `/bin/sh` on some platforms. Relative sourcing requires execution from the scripts directory.

Test signals: echoed version.
