# File Research: sources/windows/reactos/drivers/filesystems/npfs/CMakeLists.txt

This CMake file defines the ReactOS NPFS named-pipe filesystem kernel-mode driver module.

It appends all NPFS source files and the `npfs.h` header to the `SOURCE` list: cleanup, close, create, data support, file info, file object support, flush, fsctl, main, prefix support, read/read support, security support, security info, state support, structure support, volume info, wait support, write/write support, and the main header.

The build creates `npfs` as a module library with `npfs.rc`, marks it as a `kernelmodedriver`, links it with `${PSEH_LIB}`, imports `ntoskrnl` and `hal`, and configures `npfs.h` as the precompiled header for the source set.

Installation/packaging directives add the built driver to `reactos/system32/drivers` for all builds and register `npfs_reg.inf`. This file is purely build metadata; it contains no runtime NPFS logic.
