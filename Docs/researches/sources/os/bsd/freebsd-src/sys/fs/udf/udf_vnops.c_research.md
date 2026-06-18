# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/udf_vnops.c

FreeBSD UDF vnode operations implementation.

Key responsibilities:
- Defines normal UDF vnode ops and FIFO vnode ops.
- Allocates UDF vnodes, converts UDF permission bits to `mode_t`, enforces read-only write denial, and creates vnode VM objects for reads/mmap.
- Converts UDF timestamps, attributes, and file entry metadata into FreeBSD `vattr`.
- Implements reads from embedded file-entry data and extent-backed data, with clustered read support.
- Translates CS0 names via optional kernel iconv or fallback byte conversion.
- Implements directory streaming over FIDs, including fragmented FIDs, cookies, special parent entries, and deleted-entry filtering.
- Implements UDF symlink path component expansion.
- Implements strategy, bmap, cached lookup, reclaim, file-handle export, offset reads, and short/long allocation descriptor mapping with sparing table remapping.

Dependencies:
- Depends on UDF VFS state and on-disk structures from `udf.h` and `ecma167-udf.h`.
- Uses FreeBSD VFS/namecache, buffer cache, cluster read, UMA, dirent, endian, and optional iconv APIs.

Notable risks:
- Name translation without iconv degrades 16-bit characters to `.`; iconv conversion substitutes `?` for unconverted characters.
- Directory/FID parsing is defensive in places but still depends on media-derived lengths and alignment.
- Only allocation descriptor formats 0, 1, and embedded data format 3 are supported; extended descriptors and strategy 4096 are rejected.
- `udf_bmap` maps embedded data to `EOPNOTSUPP` so the pager falls back to `VOP_READ`.
- Symlink parsing supports only CS8 path components for `UDF_PATH_PATH`.
