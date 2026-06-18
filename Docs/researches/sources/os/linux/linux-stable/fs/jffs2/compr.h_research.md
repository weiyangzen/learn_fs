# File Research: sources/os/linux/linux-stable/fs/jffs2/compr.h

## Role

Private compression subsystem header for JFFS2. It defines compressor priorities, compression modes, the compressor registration structure, dispatcher APIs, and conditional module init/exit declarations.

## Key Definitions

- Compressor priorities:
  - Rubin MIPS: 10
  - Dynamic Rubin: 20
  - LZARI: 30
  - rtime: 50
  - zlib: 60
  - LZO: 80
- Rubin compressors are marked disabled for compression by default and used only for decompression.
- Compression modes:
  - `JFFS2_COMPR_MODE_NONE`
  - `JFFS2_COMPR_MODE_PRIORITY`
  - `JFFS2_COMPR_MODE_SIZE`
  - `JFFS2_COMPR_MODE_FAVOURLZO`
  - `JFFS2_COMPR_MODE_FORCELZO`
  - `JFFS2_COMPR_MODE_FORCEZLIB`
- `FAVOUR_LZO_PERCENT` sets the LZO preference threshold at 80%.

## Main Structure

`struct jffs2_compressor` carries:

- list linkage and priority;
- human-readable name and on-flash compression ID;
- `compress` and `decompress` callbacks;
- runtime `usecount` and disabled flag;
- size-mode scratch buffer and buffer size;
- compression/decompression statistics.

## API Surface

- Compressor registry: `jffs2_register_compressor()`, `jffs2_unregister_compressor()`.
- Compressor subsystem lifecycle: `jffs2_compressors_init()`, `jffs2_compressors_exit()`.
- Data APIs: `jffs2_compress()`, `jffs2_decompress()`, `jffs2_free_comprbuf()`.
- Conditional init/exit declarations for Rubin, rtime, zlib, and LZO based on Kconfig.

## Research Notes

This header is the contract between compressor implementations and the JFFS2 write/read paths. Compression identity is stored in raw inode nodes, so compatibility depends on keeping decompressor registration for historical formats even when those compressors are no longer preferred for new writes.
