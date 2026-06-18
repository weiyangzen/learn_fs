# File Research: sources/os/bsd/freebsd-src/sys/sys/kexec.h

Defines FreeBSD’s kexec load ABI aligned with Linux concepts. User-visible `struct kexec_segment` contains source buffer, source size, physical destination, and destination size. `KEXEC_ON_CRASH` and `KEXEC_SEGMENT_MAX` are defined.

Kernel-only structures stage segments through VM pages and track a loaded image’s entry point, mapping object/address/size, machine-dependent pages, and MD image data.

Userland exposes `kexec_load()`. Kernel exports machine-dependent load and reboot hooks.
