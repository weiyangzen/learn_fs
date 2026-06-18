# File Research: sources/local-fs/jfsutils/include/jfs_types.h

Base JFS type and packed descriptor definitions.

Key contents:
- Includes system integer types or defines fallback fixed-width unsigned integer aliases.
- Defines fallback `bool` if `<stdbool.h>` is unavailable.
- Defines `UniChar` as 16-bit on-disk Unicode character.
- Defines JFS `timestruc_t` with 32-bit seconds/nanoseconds.
- Defines utility macros `MIN`, `MAX`, `ROUNDUP`, and bit constants.
- Defines `pxd_t`, a packed physical extent descriptor with 24-bit length and split address fields, plus set/get macros.
- Defines `pxdlist`.
- Defines `dxd_t`, a 16-byte data extent descriptor for ACL/EA/inline/out-of-line descriptors, plus flags and aliases to PXD length/address helpers.
- Defines `component_name`.
- Defines DASD limit/usage structure and accessors.

Interactions:
- Must be included early by JFS C files.
- Relies on endian conversion macros being available when PXD/DXD accessors are used.

Research notes:
- Uses C bitfields for disk format fields; compiler layout assumptions are significant.
