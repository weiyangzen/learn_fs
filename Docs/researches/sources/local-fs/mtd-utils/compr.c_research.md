# File Research: sources/local-fs/mtd-utils/compr.c

## Purpose
User-space JFFS2 compression registry and compressor selection logic used by `mkfs.jffs2`.

## Key Elements
Implements a small Linux-style intrusive list, global compression mode state, optional compression self-checking, compressor registration/unregistration, priority changes, enable/disable by name, compressor listings, and statistics. `jffs2_compress()` supports `none`, `priority`, `size`, and `favourlzo` modes.

## Dependencies
Depends on `compr.h`, local JFFS2 constants, allocator macros mapped to libc, and external compressor modules initialized by `jffs2_zlib_init`, `jffs2_rtime_init`, and `jffs2_lzo_init`.

## Behavior/Risks
The module uses global mutable state and fixed 16 KiB buffers for formatted stats/list output. Size-selection mode allocates per-compressor buffers and transfers ownership of the winning buffer to the caller. Error handling is mostly stderr messages plus fallback to uncompressed data.
