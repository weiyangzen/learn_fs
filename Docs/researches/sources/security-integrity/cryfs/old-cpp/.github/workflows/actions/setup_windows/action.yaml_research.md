# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_windows/action.yaml

Purpose: Composite action that installs Windows dependencies needed for the legacy CryFS build and packaging job.

Important APIs and types: It has no inputs. The bash step calls Chocolatey to install Ninja and Dokany 1.3.0.1000 with developer files.

Control flow: The action sequentially runs two `choco install -y` commands.

State and persistence behavior: Mutates the Windows runner by installing build tooling and the Dokany filesystem driver/development files.

Dependencies and integration points: Used by the Windows job in `main.yaml` before Conan install, Visual Studio CMake build, tests, and WiX CPack packaging.

Risks: Dokany version and installer arguments are pinned to an old stack. Chocolatey availability and driver install behavior can change on hosted images. There is no checksum pinning here.

Test signals: Later CMake configure with `DOKAN_PATH`, Windows test binary execution, and WiX packaging success demonstrate setup correctness.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_windows/action.yaml` completely for this pass (10 lines, 275 bytes).
