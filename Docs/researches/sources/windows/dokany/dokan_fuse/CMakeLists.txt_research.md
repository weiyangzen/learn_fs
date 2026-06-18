# File Research: sources/windows/dokany/dokan_fuse/CMakeLists.txt

Build definition for the Dokan FUSE 2 compatibility DLL.

Key contents:
- Requires CMake 3.22.1 and project name `dokanfuse2`.
- Defaults build type to `Release`.
- Enables optional `FUSE_PKG_CONFIG` generation.
- Adds C++ flags `-std=c++11 -mwin32 -Wall` and `_FILE_OFFSET_BITS=64`.
- Includes local `include` and Dokan `sys` headers.
- Builds shared library `dokanfuse2` from `src/*.cpp`, `src/*.c`, and `src/*.rc`.
- Installs FUSE compatibility headers under `${includedir}/fuse`, old compatibility header under `${includedir}`, optional `fuse.pc`, and library artifacts.

Role:
- Packages Dokan’s FUSE API adapter as a libfuse-compatible Windows library.
