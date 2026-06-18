# sources/user-network-fs/libsmb2/cmake/ConfigureChecks.cmake

Purpose: This CMake module performs portability checks and generates the CMake version of `config.h`.

Important APIs and types: It uses `CheckIncludeFile`, `CheckIncludeFiles`, `CheckStructHasMember`, `CheckCCompilerFlag`, `check_include_file`, `check_include_files`, `check_struct_has_member`, `check_c_compiler_flag`, `configure_file`, and `add_definitions`.

Control flow: It checks common POSIX/network headers, optional GSSAPI/Kerberos headers based on feature flags, `netinet/tcp.h` with `sys/types.h`, platform exceptions for PS4 and Nintendo Wii/GameCube linger checks, struct members for `sa_len`, `ss_family`, and `l_linger`, adds `-Wall` when GCC accepts it, forces `_FILE_OFFSET_BITS=64`, writes `${CMAKE_CURRENT_BINARY_DIR}/config.h`, and defines `HAVE_CONFIG_H`.

State and persistence behavior: The generated `config.h` is the persistent build-tree state consumed by C sources. Compile definitions are global to the directory tree after inclusion.

Dependencies and integration points: It feeds macros used by socket, platform, crypto, and compatibility code. It is included by the root `CMakeLists.txt` except for ESP early expansion.

Risks: Header checks can be unreliable for cross-compilers without correct sysroots. Global `add_definitions` can affect external or embedded subdirectories. The `HAVE_LIBKRB5` CMake check only tests for `krb5/krb5.h`, while the autotools path checks GSSAPI headers and links `gssapi_krb5`, so feature semantics can differ.

Test signals: Inspect generated `config.h`, build all platform targets, and verify code paths guarded by `HAVE_*` compile correctly. CI across console and desktop targets is the strongest signal for this file.
