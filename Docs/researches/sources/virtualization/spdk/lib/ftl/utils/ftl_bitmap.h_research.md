# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_bitmap.h

Public API for FTL bitmaps:
- Buffer alignment constant.
- Bits-to-size and bits-to-blocks helpers.
- Create/destroy.
- Get/set/clear.
- Find first set/clear.
- Count set bits.

The bitmap object owns only its descriptor; the backing buffer is supplied by the caller.
