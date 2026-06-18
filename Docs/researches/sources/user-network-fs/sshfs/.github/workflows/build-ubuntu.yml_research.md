# sources/user-network-fs/sshfs/.github/workflows/build-ubuntu.yml

Purpose: primary Ubuntu CI workflow for building and testing sshfs with GCC/Clang and strict warning settings.

Important APIs/types/functions: build-and-test matrix over `gcc`/`clang` and `debugoptimized`/`release`; strict-warnings matrix with extra warning flags; setup-python, checkout, dependency installation, Meson `-Dwerror=true`, Ninja build, artifact upload, SSH localhost setup, FUSE checks, and pytest execution.

Control flow: each build matrix installs deps, prints versions, sets up SSH keys/server, verifies FUSE, builds with selected compiler/buildtype, uploads `build/sshfs`, and runs tests. Strict-warning jobs build with warning-focused CFLAGS but do not run FUSE tests.

State and persistence behavior: CI artifacts include binary and pytest/Meson logs.

Dependencies and integration points: Ubuntu 24.04 runner, libfuse3, GLib, OpenSSH server/client, Meson, pytest, and repository tests.

Risks: `-Dwerror=true` can fail on compiler warning drift. Runtime tests depend on runner FUSE permissions and SSH service behavior. Artifacts may expose build outputs but not secrets.

Test signals: compiler/buildtype matrix, strict warnings, localhost SSH smoke test, `/dev/fuse` check, pytest JUnit output.
