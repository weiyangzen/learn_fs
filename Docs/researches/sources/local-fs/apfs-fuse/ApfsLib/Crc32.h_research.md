# File Research: sources/local-fs/apfs-fuse/ApfsLib/Crc32.h

This header declares `Crc32`, a reusable CRC-32 calculator.

Public API includes constructor with reflect flag and optional polynomial, destructor, `SetCRC`, `GetCRC`, incremental `Calc`, and one-shot `GetDataCRC`.

Private state is the 256-entry CRC table, current CRC value, and reflect-mode flag. Private helpers perform little/reflected and big/non-reflected byte updates.

It includes `Global.h`, though the class itself only needs standard integer and size types in this header.
