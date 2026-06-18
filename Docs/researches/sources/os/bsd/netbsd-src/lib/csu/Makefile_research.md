# File Research: sources/os/bsd/netbsd-src/lib/csu/Makefile

Top-level build selector for C startup objects. It disables sanitizer instrumentation, selects an architecture directory from `CSU_MACHINE_ARCH` / `CSU_MACHINE_CPU`, special-cases `earm*`, and includes the architecture and common CSU makefiles.

The build produces startup objects such as `crt0.o`, `gcrt0.o`, `crti.o`, `crtn.o`, `crtbegin.o`, `crtend.o`, `sysident.o`, plus architecture extras like Alpha `crtfm.o`. Unsupported architectures fail the build with an explicit `.error`.
