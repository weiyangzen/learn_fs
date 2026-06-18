# sources/sync-backup/git-lfs/script/install-git-source

Purpose: small CircleCI macOS helper to build and install Git from a checked-out `git-source` directory at a requested ref.

Important commands: `git checkout "$1"`, `make --jobs=2`, and `make install`.

Control flow: changes into `git-source`, checks out the argument ref, builds with two jobs, installs, then returns to the parent directory.

State/persistence behavior: mutates the `git-source` checkout and installs Git into whatever prefix the Git build uses.

Dependencies/integration: used by macOS CI setups that need a specific Git version before running Git LFS tests.

Risks: no argument validation, no explicit `set -e`, and install permissions/prefix are inherited from the environment.

Test signals: downstream CI detects success by the installed Git version and subsequent test pass.
