# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindJeMalloc.cmake

Purpose: Finds jemalloc headers and library.

Important APIs/types/functions: Consumes CMake or environment `JEMALLOC_ROOT_DIR`; searches common prefixes, finds `jemalloc.h` under `include/jemalloc`, finds library `jemalloc`, sets `JEMALLOC_LIBRARIES` and `JEMALLOC_INCLUDE_DIRS` on success.

Control flow: Root hints and platform prefixes feed `FIND_PATH`/`FIND_LIBRARY`; standard package args determine `JEMALLOC_FOUND`.

State and persistence behavior: CMake cache variables only.

Dependencies and integration points: Optional allocator selection can include/link jemalloc using the exported variables.

Risks: Header search only uses `include/jemalloc`, which may miss installs exposing `jemalloc/jemalloc.h` differently unless include usage matches. Environment variable import can surprise hermetic builds.

Test signals: Configure with system jemalloc, custom root/env root, missing header/library, and allocator-enabled link.
