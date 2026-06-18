# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_file.c

Implements `kvm_getfiles()`, used by tools such as `pstat`, `fstat`, and `netstat` to inspect open kernel file structures.

Key behavior:
- For live/sysctl-capable descriptors, uses `CTL_KERN/KERN_FILE` to retrieve a packed file list into `kd->argspc`.
- For crash dumps, resolves `_nfiles` and `_filehead`, reads the file list head, then copies each `struct file` from kernel memory into the output buffer.
- Validates the copied count against the expected file count for dead kernels.

This module uses `kd->argspc` as reusable scratch/output storage.
