# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/ea.c

Purpose: Contains the extended-attribute set handler for the VFAT driver.

Key routine:
- `VfatSetExtendedAttributes` accepts a file object, EA buffer, and EA length, marks all parameters unused, and returns `STATUS_EAS_NOT_SUPPORTED`.

Implementation notes:
- There is no EA parsing, validation, storage, or query implementation here.
- This aligns with the rest of the VFAT code where EA query size is reported as zero and FAT12/FAT16 EA support is logged as not implemented.

Dependencies and interactions:
- Called by create/set paths when extended attributes are supplied.

Notable limitations:
- Extended attributes are explicitly unsupported for this driver.
