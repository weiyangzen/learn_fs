# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/CMakeLists.txt

This CMake file defines the ReactOS VFAT filesystem driver build.

Key contents:
- Appends all VFAT source files to `SOURCE`, including block I/O, cleanup, close, create, directory, FAT, fast I/O, FCB, flush, FSCTL, PNP, read/write, shutdown, string, volume, and `vfat.h`.
- Adds `-DKDBG` when the `KDBG` option is enabled.
- Builds `vfatfs` as a module with `vfatfs.rc`.
- Sets module type to `kernelmodedriver`.
- Links against `${PSEH_LIB}`.
- Imports `ntoskrnl` and `hal`.
- Uses `vfat.h` as the precompiled header source.
- For Xbox architecture, installs the driver to `reactos/system32/drivers` and registers `vfatfs_reg.inf`.

Notable design points:
- The file is the module-level source manifest for the VFAT FSD.
- The build is kernel-specific and depends on ReactOS kernel/hal imports and PSEH support.
