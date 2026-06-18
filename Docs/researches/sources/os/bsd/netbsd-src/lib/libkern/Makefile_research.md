# File Research: sources/os/bsd/netbsd-src/lib/libkern/Makefile

Builds the private userland `libkern` library from the kernel `sys/lib/libkern` sources. It includes NetBSD make infrastructure, marks the library private, compiles freestanding with `_STANDALONE` and `_KERNTYPES`, disables stack protector/unwind tables, and treats warnings as errors.

The selected libkern source list comes from `${S}/lib/libkern/Makefile.libkern`; the build fails early if no architecture subdirectory is available for the current machine.
