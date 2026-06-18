# File Research: sources/local-fs/xfsprogs/db/fprint.h

Purpose: declares the primitive field print callback interface.

Key contents:
- Defines `prfnc_t`, the common field print callback signature.
- Declares print functions for character arrays, numbers, structured arrays, inode time, nanoseconds, quota timers, UUIDs, and CRCs.

Interactions:
- `field.h` stores `prfnc_t` in `ftattr_t`.
- `field.c` assigns these functions to scalar and special field types.

Risks/notes:
- Print callbacks receive raw object pointer, bit offset, count, format, size, flags, array base, and array state, so callers must pass consistent field metadata.
