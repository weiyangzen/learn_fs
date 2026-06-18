# sources/user-network-fs/libsmb2/CMakeLists.txt

Purpose: This is libsmb2's primary CMake entry point. It configures project identity, install layout, feature options, platform compile definitions, dependency discovery, package metadata, examples, and the library subdirectory.

Important APIs and types: The file uses `project`, `option`, `find_package`, `include(cmake/ConfigureChecks.cmake)`, `include_directories`, `add_definitions`, `add_subdirectory`, `configure_file`, `write_basic_package_version_file`, and `install`. Feature controls include `ENABLE_EXAMPLES`, `ENABLE_LIBKRB5`, `ENABLE_GSSAPI`, `BUILD_SHARED_LIBS`, `PICO_BOARD`, `ESP_PLATFORM`, `IOP`, and `BUILD_IRX`.

Control flow: It picks a minimum CMake version based on the target platform, creates either `libsmb2` or PS2 `smb2man` project metadata, configures pkg-config data, sets install paths, chooses shared-library defaults, searches Kerberos or GSSAPI on Linux/iOS, runs configure checks, applies target-specific include paths and compatibility defines, optionally generates an MSVC `.def` file from `lib/libsmb2.syms`, adds examples when enabled, adds `lib`, and installs headers/pkg-config/CMake finder files for non-special targets.

State and persistence behavior: Generated state includes `config.h`, `libsmb2.pc`, `libsmb2-config-version.cmake`, and optionally a generated MSVC export definition. Install state includes headers, pkg-config data, and CMake package files.

Dependencies and integration points: It integrates with CMake helper modules, ESP-IDF component conventions, Raspberry Pi Pico SDK conventions, console SDK toolchains, Kerberos/GSSAPI libraries, Windows `ws2_32`, Solaris `socket`/`nsl`, examples, and `lib/CMakeLists.txt`.

Risks: The script uses many global `add_definitions` and `include_directories`, so platform settings can leak between subdirectories. Some target names and conditions are nonstandard (`EE`, `IOP`, `PS4`, `VITA`) and rely on external toolchain files. `CORE_LIBRARIES` and `core_DEPENDS` are global variables consumed by subdirectories, making ordering important.

Test signals: Good signals are successful configure/build on the CI platform matrix, generated `config.h` matching platform headers, correct optional Kerberos/GSSAPI enablement, examples linking with `smb2`, MSVC DLL export generation, and install/package discovery through the installed CMake/pkg-config metadata.
