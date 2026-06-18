# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/stub.c

This file supplies stubs and small compatibility helpers so bootstrap kernels can link without the full kernel syscall, swap, mount-auth, environment, and floating-point subsystems.

Key responsibilities:
- Stubs mount authentication/versioning, swap, pager, environment group close, syscall formatting, file descriptor allocation, and floating-point save/restore functions.
- Implements `data2txt` for converting a data segment to a text segment.
- Implements `validstat`, `fdtochan`, and `openmode` subsets needed by file operations.
- Implements boot-time `bind`, `unmount`, `chdir`, channel open/create helpers, `myreadn`, and `readfile`.
- Provides `return0` and endian helper `l2be`.

Filesystem/storage relevance:
- Allows boot code to use enough namespace and channel operations to read files, bind devices, and traverse storage/network devices without carrying the full kernel user-facing syscall layer.
