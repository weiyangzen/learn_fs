# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/errno.h

This header defines a small enum of kernel-style error identifiers.

Role:
- Provides symbolic names such as `Efidinuse`, `Eperm`, `Eio`, `Enotdir`, `Eisdir`, and mount/device errors.
- It is distinct from KFS protocol error codes in `portdat.h`.

Notable detail:
- The file is not part of the main KFS error-string table in `dat.c`; KFS protocol-facing errors use the `Ebadspc` through `Esystem` enum from `portdat.h`.
