# File Research: sources/os/linux/linux/fs/jffs2/compr.h

This header defines the JFFS2 compressor interface, compression priorities, compression modes, and compressor module init/exit declarations.

`struct jffs2_compressor` is the central plugin contract. It contains list linkage, priority, name, on-flash compression ID, optional `compress` callback, required `decompress` callback for registered formats, runtime `usecount`, disabled flag, scratch compression buffer fields used by size-comparison mode, and compression/decompression statistics.

Priority constants rank rubinmips, dynrubin, lzari, rtime, zlib, and lzo. Rubin compressors are compiled as decompression-only by default through `JFFS2_RUBINMIPS_DISABLED` and `JFFS2_DYNRUBIN_DISABLED`.

Compression modes include none, priority, best size, favour LZO, force LZO, and force ZLIB. `FAVOUR_LZO_PERCENT` defines the threshold used by `compr.c` to prefer LZO when it is close enough to the best compression ratio.

The header exposes `jffs2_compress()`, `jffs2_decompress()`, compressor registry functions, compressor subsystem init/exit, and compressed-buffer freeing. It also provides config-gated inline no-op init/exit functions when a compressor family is disabled.

Key dependencies: Linux kernel allocation/string/types headers, on-flash JFFS2 constants from `<linux/jffs2.h>`, and JFFS2 in-core inode/superblock/node structures.
