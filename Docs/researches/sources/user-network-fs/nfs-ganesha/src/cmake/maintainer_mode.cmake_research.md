# sources/user-network-fs/nfs-ganesha/src/cmake/maintainer_mode.cmake

Purpose: Defines strict maintainer/debug compiler flags and validates allowed `CMAKE_BUILD_TYPE` values.

Important APIs/types/functions: Sets `CMAKE_CXX_FLAGS_MAINTAINER`, `CMAKE_C_FLAGS_MAINTAINER`, linker flag cache entries, derived Debug flags with `-g`, allowed build type list, cache documentation for `CMAKE_BUILD_TYPE`, default Debug selection, and `USE_UNWIND`/`USE_UNWIND_ENRICHED_BT` defaults when build type is empty.

Control flow: Included during configure; it forces cache values for maintainer/debug flags, defaults empty build type to Debug, and sends an error if the selected build type is outside the allowed list.

State and persistence behavior: Mutates CMake cache aggressively with `FORCE`; no runtime state.

Dependencies and integration points: Interacts with compiler warning support, unwind/backtrace options, and all targets via global C/CXX/linker flags.

Risks: Forced `-Werror` in maintainer flags can break builds on newer compilers or third-party headers. Defaults an empty build type to Debug, which differs from some CMake conventions. Shared linker Debug flags use `CMAKE_EXE_LINKER_FLAGS_MAINTAINER`, likely intentional but worth verifying.

Test signals: Configure each allowed build type, invalid build type, empty build type, GCC/Clang warning compatibility, and builds with/without unwind dependencies.
