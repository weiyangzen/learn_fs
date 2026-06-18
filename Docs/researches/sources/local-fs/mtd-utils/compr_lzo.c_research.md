# File Research: sources/local-fs/mtd-utils/compr_lzo.c

## Purpose
JFFS2 LZO compressor adapter.

## Key Elements
When LZO is enabled, allocates LZO work memory and a worst-case temporary output buffer, uses `lzo1x_999_compress`, checks destination size before copying, and uses `lzo1x_decompress_safe`. Registers compressor name `lzo`, type `JFFS2_COMPR_LZO`, priority `80`, disabled by default.

## Dependencies
Depends on `lzo/lzo1x.h`, `linux/jffs2.h`, `compr.h`, and external `page_size`. If `WITHOUT_LZO` is defined, init/exit become no-ops.

## Behavior/Risks
Compression uses global work buffers, so it is not reentrant. LZO is registered disabled, requiring explicit enablement by name or policy.
