## sources/storage-engines/wiredtiger/src/utilities/CMakeLists.txt

Purpose: defines the `wt` command-line utility target and its source list for the CMake build. It gathers the command dispatcher, individual command implementations, shared utility helpers, and optional Antithesis dependency into one executable.

Important APIs/types/functions: declares `sources` containing `util_main.c`, command files such as `util_dump.c`, `util_load.c`, `util_backup.c`, and shared files such as `util_misc.c` and `util_verbose.c`. It calls `add_executable(wt ${sources})`, applies `${COMPILER_DIAGNOSTIC_C_FLAGS}`, adds include paths for `src/include` and generated `config`, links `wt::wiredtiger`, optionally links `wt::voidstar`, sets `RUNTIME_OUTPUT_DIRECTORY` to `${CMAKE_BINARY_DIR}`, and installs the binary to `bin`/`${CMAKE_INSTALL_BINDIR}`.

Control flow: configure-time logic builds the source list, declares the target, configures compilation/linking, applies backward-compatible output placement expected by tests, and registers install rules. There is no runtime control flow in this file.

State and persistence behavior: affects build-system state: target source membership, include/link dependencies, output path, and install destination. The top-level runtime output placement is a compatibility contract for existing tests and examples that expect `wt` at the build root.

Dependencies and integration points: integrates with the main WiredTiger CMake target namespace, generated configuration headers, compiler diagnostic flag setup, Antithesis optional build flag, test harness expectations, and installation packaging.

Risks: omitting a command source from the list can compile a dispatcher reference without implementation or silently drop a utility subcommand. Moving `RUNTIME_OUTPUT_DIRECTORY` can break tests/scripts that execute `${CMAKE_BINARY_DIR}/wt`. The install rule uses both `RUNTIME DESTINATION bin` and `DESTINATION ${CMAKE_INSTALL_BINDIR}`; changes should be checked against CMake install semantics and packaging expectations.

Test signals: successful CMake configure/build of target `wt`, ability to run `${builddir}/wt -V`, command dispatch smoke tests, Antithesis-enabled builds when `ENABLE_ANTITHESIS` is set, and install packaging checks that place the binary in the expected bindir.
