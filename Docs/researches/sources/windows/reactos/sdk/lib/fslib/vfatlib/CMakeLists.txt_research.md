# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/CMakeLists.txt

This build file defines the VFAT filesystem library target.

Core contents:
- Lists checker sources: `check/boot.c`, `check/check.c`, `check/common.c`, `check/fat.c`, `check/file.c`, `check/io.c`, and `check/lfn.c`.
- Lists formatter/common sources: `common.c`, `fat12.c`, `fat16.c`, `fat32.c`, `vfatlib.c`, and `vfatlib.h`.
- Builds `vfatlib`, depends on `xdk`, and configures `vfatlib.h` as the precompiled header.

Risk points:
- This group includes only part of the target’s source list, so behavior depends on additional VFAT files outside this work item.
- Vendored dosfsck-style checker code is compiled together with ReactOS-specific formatting code.
