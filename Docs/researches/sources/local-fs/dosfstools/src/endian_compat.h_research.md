# File Research: sources/local-fs/dosfstools/src/endian_compat.h

Endian conversion compatibility header.

Behavior:
- Includes `<endian.h>` when available.
- Else includes `<sys/endian.h>` when available.
- Else, on Apple platforms with `libkern/OSByteOrder.h`, maps `htobe*`, `htole*`, `be*toh`, and `le*toh` macros to `OSSwap...` functions.
- Emits a preprocessor error if no endian support is available.

Role:
- Supplies consistent little-endian conversions for FAT on-disk structures.
- Included by `fsck.fat.h`, so most FAT metadata code gets these conversions transitively.
