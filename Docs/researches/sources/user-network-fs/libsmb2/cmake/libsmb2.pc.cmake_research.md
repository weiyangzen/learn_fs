# sources/user-network-fs/libsmb2/cmake/libsmb2.pc.cmake

Purpose: This template generates the pkg-config file for CMake installs of libsmb2.

Important APIs and types: It defines pkg-config fields `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Description`, `Version`, `Requires`, `Conflicts`, `Libs`, and `Cflags`, using CMake substitutions such as `@CMAKE_INSTALL_PREFIX@`, `@INSTALL_LIB_DIR@`, `@INSTALL_INC_DIR@`, and `@PROJECT_VERSION@`.

Control flow: The root `CMakeLists.txt` configures this template into the build directory and installs it under the configured pkg-config directory for normal non-Pico/non-special builds.

State and persistence behavior: The generated `.pc` file is installed metadata consumed by downstream build systems. It records the install prefix and link/include flags.

Dependencies and integration points: Downstream consumers using `pkg-config --libs --cflags libsmb2` rely on this file. `FindSMB2.cmake` can also use pkg-config values indirectly.

Risks: `Requires` is empty even when optional Kerberos/GSSAPI or platform libraries are linked, so static consumers may miss transitive dependencies. The template hardcodes `-lsmb2` and does not expose optional compile definitions.

Test signals: After install, `pkg-config --modversion libsmb2`, `--cflags`, and `--libs` should return usable values, and a small external program should compile and link using those flags.
