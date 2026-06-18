# sources/user-network-fs/sshfs/test/appveyor-build.sh

Purpose: AppVeyor helper script that performs a Meson/Ninja build in an architecture-specific directory.

Important APIs/types/functions: detects `uname -m`, creates `build-$machine`, runs `meson ..`, then `ninja`.

Control flow: `set -e` aborts on the first failing command.

State and persistence behavior: creates a build directory under the repository checkout in CI.

Dependencies and integration points: invoked by `.appveyor.yml` for both Cygwin environments.

Risks: fails if build directory already exists. It does not run tests or pass warning flags.

Test signals: successful AppVeyor build for each architecture.
