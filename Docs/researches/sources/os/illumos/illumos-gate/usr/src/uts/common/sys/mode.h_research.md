# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mode.h

Purpose: Provides kernel conversion macros between vnode types and encoded file type/mode bits used by `stat(2)` and `mknod(2)`.

Key definitions:
- External conversion tables: `iftovt_tab[]`, `vttoif_tab[]`.
- `IFTOVT(M)`: mode bits to `enum vtype`.
- `VTTOIF(T)`: vnode type to inode/stat file type bits.
- `MAKEIMODE(T, M)`: combines vnode type with permission/mode bits.

Important detail: Only visible for `_KERNEL` or `_FAKE_KERNEL`.

Relevance to subset A: Direct VFS/filesystem helper for translating vnode metadata to user-visible mode bits.
