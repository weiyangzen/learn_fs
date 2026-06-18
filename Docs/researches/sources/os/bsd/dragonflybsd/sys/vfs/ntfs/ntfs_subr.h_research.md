# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_subr.h

This header defines `struct ntvattr`, the in-memory representation of one NTFS attribute, including type, name, compression fields, data length/allocation, VCN range, index, resident data pointer, runlist arrays, or typed overlays for file name/index root/index allocation data.

It also declares the NTFS helper API implemented mostly in `ntfs_subr.c`: fixups, run parsing, attribute reads/writes, size/time queries, directory lookup/enumeration, attribute conversion/freeing, ntnode/fnode lifetime management, toupper table management, and charset conversion.

Research notes: some declared functions are disabled or absent in the implementation (`ntfs_parserun`, `ntfs_runtocn`, `ntfs_loadntvattrs`, `ntfs_findntvattr`), so this header includes legacy API surface beyond active code.
