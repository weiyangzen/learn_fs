# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindEPOLL.cmake

Purpose: Detects epoll support, with FreeBSD-based platforms treated as supported via emulation.

Important APIs/types/functions: Uses `BSDBASED`, `check_include_files("sys/epoll.h" EPOLL_HEADER)`, `check_function_exists(epoll_create EPOLL_FUNC)`, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS(EPOLL ...)`.

Control flow: If `BSDBASED` is true, sets `EPOLL_FOUND ON` and returns. Otherwise it requires both header and function checks.

State and persistence behavior: CMake check result variables only.

Dependencies and integration points: Event-loop/network code conditions on `EPOLL_FOUND`.

Risks: The documented `EPOLL_PATH_HINT` is not used. `check_function_exists` may need libraries on unusual platforms. FreeBSD emulation is assumed without validating the emulation header/API here.

Test signals: Configure on Linux, FreeBSD, and a non-epoll Unix; verify generated feature decisions.
