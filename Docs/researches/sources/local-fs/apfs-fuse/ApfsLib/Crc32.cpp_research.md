# File Research: sources/local-fs/apfs-fuse/ApfsLib/Crc32.cpp

This file implements a table-driven CRC-32 helper with reflected and non-reflected modes.

The constructor builds the 256-entry lookup table from the supplied polynomial, reversing the polynomial bit order when reflected mode is requested. `Calc()` dispatches each byte to little/reflected or big/non-reflected update logic.

`GetDataCRC()` sets the initial XOR value, processes a buffer, and returns final-XOR-adjusted CRC.

The class is used by disk image and GPT-related code, not APFS block checksum verification, which uses APFS Fletcher-style checksum utilities elsewhere.
