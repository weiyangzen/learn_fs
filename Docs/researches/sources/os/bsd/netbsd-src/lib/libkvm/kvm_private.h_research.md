# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_private.h

Private `libkvm` header defining the internal `struct __kvm` descriptor and cross-module helper prototypes.

Key fields:
- Open file descriptors for physical memory/dump, virtual memory, swap, and namelist.
- Aliveness mode: dead dump, live files, or sysctl-only.
- Cached process/LWP/file/argv buffers and lengths.
- Crash dump headers, CPU data, dump offset, mmap pointer/size.
- Machine-dependent virtual translation state and cached VM page lookup state.
- Device-aligned I/O scratch buffer and kernel name.

It also defines `ISALIVE`, `ISKMEM`, `ISSYSCTL`, `KREAD`, and `KVM_ALLOC`, which are used throughout `libkvm`.
