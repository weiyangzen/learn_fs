# File Research: sources/windows/reactos/drivers/filesystems/fastfat/CMakeLists.txt

This CMake file defines the ReactOS `fastfat` filesystem driver build target.

It appends the FAT driver source list, including create/read/write, cache support, directory support, volume info, PnP, shutdown, locking, verification, work queue, and `fatprocs.h`.

It builds `fastfat` as a module with `fastfat.rc`, marks it as a `kernelmodedriver`, links `${PSEH_LIB}` and `memcmp`, imports `ntoskrnl` and `hal`, configures `fatprocs.h` as the precompiled header, and installs the driver to `reactos/system32/drivers`.

Research notes: this file contains build orchestration only; it has no runtime filesystem logic but controls which source files participate in the fastfat driver.
