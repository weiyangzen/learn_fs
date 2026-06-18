# File Research: sources/teaching/os161/kern/include/kern/errno.h

Defines OS/161 numeric error codes shared with userland and assembler.

Key filesystem-relevant errors:
- `ENOMEM`, `ENAMETOOLONG`, `EINVAL`, `EACCES`.
- `ENOTDIR`, `EISDIR`, `ENOENT`, `EEXIST`.
- `ENODEV`, `ENXIO`, `EBUSY`, `EIO`, `ESPIPE`.
- `EROFS`, `ENOSPC`, `EFBIG`, `EFTYPE`, `ENOTSUP`.

Relevance:
- SFS and semfs return these codes from vnode/fs operations, allocation paths, mount validation, and unsupported operations.
