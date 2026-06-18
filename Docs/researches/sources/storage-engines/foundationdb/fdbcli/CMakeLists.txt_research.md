# sources/storage-engines/foundationdb/fdbcli/CMakeLists.txt

Purpose: Defines the `fdbcli` executable target, its include path, link dependencies, install behavior, sanitizer-specific link behavior, platform-specific linenoise usage, and fdbcli integration tests.

Important APIs/types/functions: CMake macros/functions include `fdb_find_sources`, `add_flow_target`, `target_include_directories`, `target_link_libraries`, `target_link_options`, `fdb_install`, `add_custom_target`, `add_dependencies`, and `add_fdbclient_test`. It links `fdbcli` against `fdbctl`, `fdbclient`, `SimpleOpt`, and non-Windows `linenoise`.

Control flow: Source files are discovered into `FDBCLI_SRCS`, then `add_flow_target(EXECUTABLE NAME fdbcli ...)` creates the executable. The target includes `fdbcli/include`. If UBSan is enabled, `-rdynamic` is added so typeinfo symbols agree between fdbcli and external `libfdb_c` clients for vptr checks. Non-Windows builds link linenoise. Install behavior differs between debug-package and stripped-package modes. Test registration is enabled only outside Windows and IDE-only builds, depends on `external_client`, and skips all four fdbcli Python test lanes under ASan.

State and persistence behavior: This file controls build graph and installation artifacts only. It persists no runtime state, but it determines whether installed clients use a stripped package binary or direct target output.

Dependencies and integration points: Integrates fdbcli into the broader FoundationDB Flow/CMake build system, package installation, external client build, and `fdbcli/tests/fdbcli_tests.py`. The external-client variants pass `--external-client-library` pointing at `bindings/c/libfdb_c_external.so`.

Risks: Automatic source discovery means new files under the directory are compiled unless excluded by the macro. Test coverage is intentionally absent under ASan because of known failures/timeout; regressions specific to ASan builds may be missed. Install behavior depends on `strip_only_fdbcli` existing when debug packages are disabled.

Test signals: Build success for `fdbcli`, package install generation, UBSan symbol behavior, non-Windows linenoise linking, and four non-ASan fdbclient tests: single/multi-process native and single/multi-process external-client fdbcli tests.
