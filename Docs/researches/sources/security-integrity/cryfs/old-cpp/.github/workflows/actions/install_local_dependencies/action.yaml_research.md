# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/install_local_dependencies/action.yaml

Purpose: Composite GitHub Action that manually builds and installs legacy C++ dependencies from source on CI when the matrix requests local-system dependency coverage.

Important APIs and types: The action has no inputs. Its bash script determines `NUMCORES`, downloads range-v3 0.11.0, spdlog 1.8.5, and Boost 1.75.0, validates hard-coded SHA-512 sums, builds with CMake or Boost.Build, and installs with `sudo make install` or `sudo ./b2 ... --prefix=/usr install`.

Control flow: The script runs with `set -v`, detects core count using `nproc` with `sysctl` fallback, then performs download, checksum, extraction, build, install, and cleanup for range-v3 and spdlog. It then downloads Boost from SourceForge, verifies checksum, bootstraps selected libraries, and installs shared PIC libraries to `/usr`.

State and persistence behavior: It mutates the CI runner by installing headers/libraries into system locations. Temporary tarballs and source directories are created under `~` and mostly removed. Failed checksum validation exits the job.

Dependencies and integration points: Used by `main.yaml` local-dependencies matrix jobs with `DependenciesFromLocalSystem.cmake`. It assumes `wget`, `sha512sum`, `tar`, CMake, Make, sudo, and compiler toolchains are present.

Risks: Source URLs and checksums are pinned but rely on network availability and SourceForge redirect behavior. Installing into `/usr` can affect later build discovery and cache isolation. The bash test `[ ! -n "$NUMCORES" ]` is old style but functional. Dependencies are not cached despite a TODO, so this path is slow.

Test signals: CI success through this action is the signal: correct checksums, successful configure/build/install, and later CMake local dependency discovery.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/install_local_dependencies/action.yaml` completely for this pass (76 lines, 2746 bytes).
