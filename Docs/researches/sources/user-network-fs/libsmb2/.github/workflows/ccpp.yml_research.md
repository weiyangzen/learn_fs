# sources/user-network-fs/libsmb2/.github/workflows/ccpp.yml

Purpose: This GitHub Actions workflow is the main C/C++ build matrix for libsmb2. It validates the project across Linux, Windows/MSVC, PS2, Vita, PS3 PPU, PS4, Switch, 3DS, Wii, GameCube, Wii-U, DS, and Amiga targets.

Important APIs and types: The file uses GitHub Actions jobs, `actions/checkout@v4`, platform containers such as `ps2dev/ps2dev`, `vitasdk/vitasdk`, `devkitpro/*`, and `amigadev/crosstools`, plus CMake and `Makefile.platform`/platform-specific makefiles. The Linux job installs `libkrb5-dev`, configures `cmake -S . -B build`, and builds the tree. Windows uses the Visual Studio 17 2022 generator.

Control flow: The workflow runs on push and pull request. Most jobs checkout sources, install platform dependencies or rely on a container, then invoke one or more platform build targets followed by `clean`. The PS3 and PS4 jobs manually fetch or configure SDK package sources before building.

State and persistence behavior: State is ephemeral CI workspace state: downloaded SDK archives, CMake build directories, package manager state, and environment variables such as `PS3DEV` and `PSL1GHT`. No artifacts are persisted by this workflow.

Dependencies and integration points: It integrates the root CMake build, `Makefile.platform`, console SDK images, distro package managers, and platform makefiles under `lib/`. It is a broad regression signal for conditional compile definitions in `CMakeLists.txt`, compatibility shims, and platform-specific source directories.

Risks: Several jobs depend on mutable `latest` container tags, external archive URLs, third-party package repositories, and unpinned checkout actions. Some jobs run `make ... clean` in the same command, which proves the target can build and clean but may hide artifact inspection opportunities. Platform SDK changes can break CI without code changes.

Test signals: A green matrix proves the project configures and compiles on mainstream and embedded/console targets. Failures localize portability regressions in compile definitions, missing compatibility APIs, SDK drift, package availability, or build-system target wiring.
