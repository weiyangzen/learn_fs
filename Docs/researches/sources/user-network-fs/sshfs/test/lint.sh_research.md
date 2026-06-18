# sources/user-network-fs/sshfs/test/lint.sh

Purpose: lint helper for CI/local validation using pre-commit.

Important APIs/types/functions: installs `pre-commit` with `pip3 --user` and runs `pre-commit run --all-files --show-diff-on-failure`.

Control flow: `set -e` aborts on install or hook failure.

State and persistence behavior: modifies user-local Python package state and may create pre-commit caches; hooks may report diffs.

Dependencies and integration points: used by Travis lint job; consumes `.pre-commit-config.yaml`.

Risks: installing into user site during CI can be version-sensitive. No pin for `pre-commit` itself.

Test signals: successful hook execution with no diffs.
