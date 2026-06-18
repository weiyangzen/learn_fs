# sources/sync-backup/casync/test/meson-check-help.sh

Purpose: smoke-tests command help output under Meson.

Important APIs/types/functions: shell script invokes built binaries with help/version-like arguments and expects successful output.

Control flow/state: no persistent state; exits nonzero on command failure under `set -e` style behavior.

Dependencies/integration: wired from `test/meson.build` as a lightweight test that catches missing binaries or broken option parsing.

Risks/test signals: only validates shallow CLI availability, not full behavior. It can be sensitive to builddir substitutions and executable paths.

Source research group: `subset-b-009122`.
