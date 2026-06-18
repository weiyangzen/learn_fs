# sources/user-network-fs/nfs-ganesha/src/cmake/goption.cmake

Purpose: Provides custom option macros that distinguish defaulted options from explicit user requests, allowing missing dependencies to be optional or required depending on command-line intent.

Important APIs/types/functions: `goption(OPTNAME DESC DEFVAL)` stores cache value `DEFAULT_ON` or `DEFAULT_OFF` with allowed strings `ON OFF`. `gopt_test(OPTNAME)` normalizes the option to `ON`/`OFF` and sets `${OPTNAME}_REQUIRED` to empty for defaults or `REQUIRED` for explicit user settings.

Control flow: Callers define options with `goption`, then call `gopt_test` before `find_package` or custom dependency checks. Later code uses `${OPTNAME}_REQUIRED` to decide fatal vs warning/disable behavior.

State and persistence behavior: CMake cache variables are mutated and sometimes forced. The default sentinel values persist until `gopt_test` normalizes them.

Dependencies and integration points: Central to FSAL/feature option handling throughout the CMake tree, especially optional dependencies.

Risks: Macro conditionals rely on dynamic variable expansion and string matches; malformed cache values can lead to surprising branches. The example comment has a duplicated `elseif (USE_FSAL_TEST_REQUIRED)` where an `else` was probably intended. Cache forcing explicit values can surprise repeated configure runs.

Test signals: Configure with omitted option, `-DOPT=ON`, `-DOPT=OFF`, invalid string, and dependency missing to verify required/default behavior.
