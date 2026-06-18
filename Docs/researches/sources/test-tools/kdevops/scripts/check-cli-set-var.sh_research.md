# sources/test-tools/kdevops/scripts/check-cli-set-var.sh

Purpose: checks whether an environment variable is present and prints `y`/`n`.

Important APIs/types/functions: `which env`, `env | grep ^NAME= | head -1 | awk`.

Control flow: requires exactly one argument; returns `n` if `env` is unavailable or variable is absent, otherwise `y`.

State/persistence behavior: read-only environment inspection.

Dependencies/integration: used by Kconfig/Make checks for CLI-provided variables.

Risks/test signals: grep pattern is susceptible to regex metacharacters in the variable name, though variable names are normally simple. Test signals are `y` for exported variables and `n` otherwise.
