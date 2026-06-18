# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_macos/action.yaml

Purpose: Composite action that installs macOS dependencies for the legacy C++ CI matrix.

Important APIs and types: Input `extra_homebrew_packages` lets each compiler row request a Homebrew compiler package. The step runs `brew install ninja macfuse libomp ccache md5sha1sum` plus that input.

Control flow: A single bash step invokes Homebrew installation.

State and persistence behavior: Mutates the ephemeral macOS runner by installing packages into Homebrew-managed locations.

Dependencies and integration points: Called by macOS rows in `main.yaml`. It supports CMake/Ninja builds, FUSE integration, OpenMP, ccache, and checksum utilities.

Risks: Homebrew package availability for old compiler versions is unstable, and `main.yaml` already excludes clang 7 because it disappeared. macFUSE installation can be sensitive to runner image policy.

Test signals: Successful brew install and later compiler/test execution in macOS matrix jobs are the only signals.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_macos/action.yaml` completely for this pass (13 lines, 384 bytes).
