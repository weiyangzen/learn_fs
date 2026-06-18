# File Research: sources/windows/reactos/drivers/filesystems/msfs/CMakeLists.txt

This build file defines the ReactOS mailslot filesystem driver module `msfs`.

It builds from `create.c`, `finfo.c`, `fsctrl.c`, `msfs.c`, `msfssup.c`, `rw.c`, and `msfs.h`, adds `msfs.rc`, marks the target as a kernel-mode driver, links against `ntoskrnl` and `hal`, configures `msfs.h` as the precompiled header, installs the driver under `reactos/system32/drivers`, and registers `msfs_reg.inf`.

Research notes:
- The module is self-contained inside the listed MSFS files.
- No external filesystem library is linked beyond kernel/HAL imports.
