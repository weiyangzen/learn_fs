# File Research: sources/local-fs/jfsutils/libfs/utilsubs.h

This header declares small utility APIs and defines `fopen_excl()` inline.

Contents:
- Prototypes for `log2shift()`, `prompt()`, and `more()`.
- `static inline FILE *fopen_excl(const char *path, const char *mode)`, which opens `path` with `O_RDWR | O_EXCL` and wraps the descriptor in `fdopen()`.
- Prototypes for mount/type helpers `Is_Device_Mounted()` and `Is_Device_Type_JFS()` implemented elsewhere.

Notes:
- `fopen_excl()` ignores the requested open mode for the `open()` call and always opens read/write.
- `O_EXCL` without `O_CREAT` is not a portable locking primitive; behavior depends on platform/device semantics.
