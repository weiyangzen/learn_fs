# sources/security-integrity/cryfs/old-cpp/.github/workflows/main.yaml

Purpose: Defines the legacy CryFS GitHub Actions CI pipeline for Linux, macOS, and Windows builds, tests, sanitizer variants, clang-tidy, dependency caching, and Windows installer artifacts.

Important APIs and types: The workflow triggers on push and pull request. It has `linux_macos` and `windows` jobs. The Linux/macOS matrix spans old macOS/Ubuntu versions, GCC/Clang versions, Debug/Release/RelWithDebInfo, local-dependency builds, Werror, no-compatibility, ASAN, UBSAN, TSAN, and clang-tidy rows. Composite actions in `.github/workflows/actions` provide setup/build/test behavior. The workflow also uses the pinned S3 cache action `leroy-merlin-br/action-s3-cache@8d750...`.

Control flow: Linux/macOS jobs check out code, run OS-specific setup, optionally install local dependencies, upgrade/install pip and Conan 1.59, restore pip/ccache/Conan caches, configure ccache, hash flags, build with composite actions, optionally run clang-tidy with fixes artifact, save caches on push, and run tests. Windows jobs install Dokany/Ninja, install Conan, restore caches, configure/build with Visual Studio 2019 and CMake, run selected test executables, run CPack WiX, and upload MSI artifacts.

State and persistence behavior: CI state includes build directories, ccache, Conan caches under configured homes, pip caches, generated clang-tidy diff artifacts, and MSI artifacts. On push, write-capable cache credentials from secrets save caches; read-only S3 credentials are embedded for PR cache reads.

Dependencies and integration points: Integrates all old C++ build helpers, CMake dependency resolution, Conan 1.x, ccache, sanitizer env vars, Visual Studio, Dokany, WiX packaging, and the test layout. It is the top-level consumer of the setup/build/test composite actions.

Risks: The workflow targets obsolete runner images and toolchain versions (`ubuntu-18.04`, `macos-10.15`, old compiler packages, `actions/checkout@v1`, `actions/upload-artifact@v2`, deprecated `set-output`, deprecated `apt-key`). Public read-only S3 cache credentials are intentionally embedded but still expand the external trust surface. Cache restore is `continue-on-error`, which improves resilience but can hide cache corruption. Several test exclusions mark known platform/sanitizer gaps.

Test signals: Matrix success gives broad compiler/platform coverage. Special signals include Werror build-only rows, ASAN/UBSAN/TSAN test rows with filters, no-compatibility builds, clang-tidy diff artifact on failure, Windows test executable success, and WiX installer upload.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/main.yaml` completely for this pass (610 lines, 30103 bytes).
