# sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromLocalSystem.cmake

Purpose: Alternative dependency configuration that finds range-v3, Boost, and spdlog from the local system instead of Conan.

Important APIs and types: Defines `check_target_is_not_from_conan`, uses `find_package(range-v3 REQUIRED)`, `find_package(Boost 1.65.1 REQUIRED COMPONENTS filesystem system thread chrono program_options)`, and `find_package(spdlog REQUIRED)`, then exposes the same `CryfsDependencies_*` interface targets as the Conan config.

Control flow: The file warns if discovered include directories look like Conan paths, creates local dependency interface targets, links Boost components and `rt` on Linux, and leaves version compatibility to the local packages.

State and persistence behavior: No files are written. Configure-time state consists of imported package targets and interface targets.

Dependencies and integration points: Used by CI's local-dependencies matrix rows and by users passing `-DDEPENDENCY_CONFIG=../cmake-utils/DependenciesFromLocalSystem.cmake`. It preserves the same target names as the default dependency file so the rest of the build remains unchanged.

Risks: The comments explicitly state local dependency versions are not officially supported. The Conan-leak warning is heuristic and only inspects include directories. Boost library ABI/version mismatches are a practical risk.

Test signals: CI local-dependency jobs on Ubuntu 18.04 and 20.04 are the primary signal that this configuration remains viable.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromLocalSystem.cmake` completely for this pass (61 lines, 2822 bytes).
