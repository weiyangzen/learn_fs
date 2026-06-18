# File Research: sources/os/bsd/netbsd-src/lib/libnvmm/Makefile

Builds `libnvmm` from `libnvmm.c`, installs `nvmm.h`, and installs the `libnvmm.3` manual page.

Important build details: `WARNS=5`; `COPTS.libnvmm.c` suppresses dangling-pointer warnings with `${CC_WNO_DANGLING_POINTER}`.

The library is a thin userland interface to the NVMM hypervisor device.
