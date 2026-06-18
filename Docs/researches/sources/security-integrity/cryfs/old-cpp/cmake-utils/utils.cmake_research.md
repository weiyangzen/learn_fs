# sources/security-integrity/cryfs/old-cpp/cmake-utils/utils.cmake

Purpose: Collects legacy CMake utility functions for C++ standard activation, style warnings, static analysis tool integration, Boost linking, compiler version checks, and target architecture detection.

Important APIs and types: Public functions include `target_activate_cpp14`, `target_enable_style_warnings`, `target_add_boost`, `require_gcc_version`, `require_clang_version`, and `get_target_architecture`. It also discovers `clang-tidy` and include-what-you-use when configured.

Control flow: `target_activate_cpp14` sets C++14 except MSVC uses C++17 for range-v3, applies libc++ on Apple Clang, and enables exports for Boost stacktrace. Warning setup adds compiler-specific warning flags, optional `-Werror`, and optional target properties for clang-tidy/IWYU. `target_add_boost` links `CryfsDependencies_boost` and defines `BOOST_THREAD_VERSION=4`. Version checks inspect compiler IDs/versions and fatal on too-old compilers. Architecture detection delegates to `TargetArch.cmake`.

State and persistence behavior: No files are written directly. It mutates CMake target properties and configure variables.

Dependencies and integration points: Included by project CMake files throughout old-cpp. It relies on dependency config files defining `CryfsDependencies_boost`, and on optional tools being available when corresponding flags are enabled.

Risks: MSVC C++17 special-casing means the function name is historical, not literal. Warning sets are incomplete and old. `USE_CLANG_TIDY` and `USE_IWYU` become fatal if tools are missing. Apple-only libc++ handling means Linux clang uses libstdc++ despite some debug macro assumptions elsewhere.

Test signals: Build success across compiler matrix rows, Werror rows, and clang-tidy workflow rows are the practical validation signals.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/utils.cmake` completely for this pass (141 lines, 6148 bytes).
