# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_linux/action.yaml

Purpose: Composite action that prepares Linux GitHub runners with required packages and entropy behavior for legacy CryFS CI.

Important APIs and types: Inputs are `os` and `extra_apt_packages`. It edits APT retry configuration, optionally adds LLVM apt repositories for Ubuntu 18.04/20.04, installs base packages plus the requested compiler package, and replaces `/dev/random` with a copy of `/dev/urandom`.

Control flow: For older Ubuntu versions it downloads the LLVM GPG key, creates `/etc/apt/sources.list.d/clang.list`, writes llvm-toolchain repo lines, then runs `apt-get update` and installs Ninja, libcurl, FUSE dev headers, ccache, and compiler packages. A second step copies `/dev/urandom` to `/dev/random`.

State and persistence behavior: Mutates the runner's apt configuration, installed packages, and device node/file state. These changes are confined to the ephemeral CI VM.

Dependencies and integration points: Used by Linux matrix rows in `main.yaml` before dependency cache and build actions. It assumes sudo, wget, apt, and Ubuntu runner images.

Risks: Uses deprecated `apt-key` and plain HTTP LLVM apt sources. Replacing `/dev/random` is invasive and could hide entropy-related behavior. The repo setup is hard-coded for clang 11 and old Ubuntu releases.

Test signals: Successful package install and later compiler/CMake discovery show setup worked. Faster tests that otherwise block on entropy are the intended secondary signal.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_linux/action.yaml` completely for this pass (41 lines, 2070 bytes).
