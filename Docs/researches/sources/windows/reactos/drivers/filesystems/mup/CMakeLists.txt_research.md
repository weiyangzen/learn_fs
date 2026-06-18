# File Research: sources/windows/reactos/drivers/filesystems/mup/CMakeLists.txt

This build file defines the ReactOS Multi UNC Provider driver module `mup`.

It builds `dfs.c`, `mup.c`, `dfs.h`, and `mup.h` into a kernel-mode driver, links the PSEH library plus `ntoskrnl` and `hal`, uses `mup.h` as the precompiled header, and installs the resulting driver under `reactos/system32/drivers`.

Research notes:
- The MUP module includes DFS stubs, but DFS is not functionally implemented in this group.
- PSEH is needed because `mup.c` uses structured exception handling macros.
