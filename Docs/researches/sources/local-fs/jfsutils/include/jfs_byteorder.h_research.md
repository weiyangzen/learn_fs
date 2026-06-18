# File Research: sources/local-fs/jfsutils/include/jfs_byteorder.h

Endian conversion helper macros for little-endian JFS on-disk fields.

Key contents:
- Includes platform byte-order headers selected by configure.
- Defines byte-swap macros for 16-, 24-, 32-, and 64-bit values.
- Defines CPU-to-little-endian and little-endian-to-CPU macros as identity on little-endian hosts and swap on big-endian hosts.
- Emits compile-time error for unsupported byte order.

Interactions:
- Used by packed extent/address macros in `jfs_types.h`, `jfs_dtree.h`, and `jfs_xtree.h`.

Research notes:
- Uses GNU statement-expression style macros, so portability assumes compatible compiler behavior.
