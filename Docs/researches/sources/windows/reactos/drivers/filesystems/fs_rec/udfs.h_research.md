# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/udfs.h

This header contains UDF/ECMA volume-structure descriptor identifiers and the descriptor layout used by the recognizer.

It defines standard identifiers:
- `NSR02` for ECMA-167 revision 2 UDF namespace.
- `NSR03`, `BEA01`, `BOOT2`, `CD001`, `CDW02`, and `TEA01` for ECMA-167 revision 3 / related descriptor recognition.

`VOLSTRUCTDESC` is a 2048-byte descriptor with one-byte type, five-byte identifier, one-byte version, and remaining data payload.

Research notes:
- This file is narrowly scoped to recognition.
- The descriptor size implicitly matches common optical-media sector sizing.
- `VSD_STD_ID_LEN` is five, matching all identifiers used by `udfs.c`.
