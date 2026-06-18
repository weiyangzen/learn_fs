# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindExecInfo.cmake

Purpose: Finds `execinfo.h` and libexecinfo for backtrace support on platforms where it is separate.

Important APIs/types/functions: Sets `EXECINFO_INCLUDE_DIR`, `EXECINFO_LIBRARY`, and `EXECINFO_FOUND`; emits status or fatal error based on find mode.

Control flow: Simple header/library search, manual found handling, and optional fatal if required.

State and persistence behavior: CMake cache variables only.

Dependencies and integration points: Backtrace/unwind diagnostics may consume these variables.

Risks: Required-variable name uses `ExecInfo_FIND_REQUIRED` while the module file is `FindExecInfo.cmake`; CMake package-name casing can make this brittle. It does not use `FindPackageHandleStandardArgs`.

Test signals: Configure on glibc where execinfo may not require a separate library, FreeBSD with libexecinfo, and required missing cases.
