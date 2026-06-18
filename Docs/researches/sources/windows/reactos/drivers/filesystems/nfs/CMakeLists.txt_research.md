# File Research: sources/windows/reactos/drivers/filesystems/nfs/CMakeLists.txt

This build file defines the ReactOS NFSv4.1 mini-redirector driver module `nfs41_driver`.

It builds `nfs41_driver.c`, `nfs41_debug.c`, `nfs41_driver.h`, and `nfs41_debug.h`, includes headers from `dll/np/nfs`, defines `RDBSS_TRACKER`, and links against `ntoskrnl_vista`, `rdbsslib`, `rxce`, `copysup`, `memcmp`, PSEH, `ntoskrnl`, and `hal`.

Compiler-specific suppressions disable `-Wno-switch` for GCC/Clang and `-Wno-unused-value` for Clang. The module is installed under `reactos/system32/drivers` and registers `nfs41_reg.inf`.

Research notes:
- This is an RDBSS-based network mini-redirector, not a standalone local filesystem.
- The debug file in this group is auxiliary support for the broader NFS driver.
