# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_conv.c

Provides UTF-8 filename conversion callbacks for NTFS.

Key points:
- `ntfs_utf8_wget()` decodes one UTF-8 character to NTFS `wchar` using NetBSD unicode helpers.
- `ntfs_utf8_wput()` encodes an NTFS wide character to UTF-8.
- `ntfs_utf8_wcmp()` compares two wide characters directly.

Role:
- These callbacks are installed into `ntfsmount` during mount.
- Used by lookup and readdir code to compare and emit NTFS Unicode names.

Limitations:
- The file notes UTF-8 only; no alternate charset support is implemented here.
