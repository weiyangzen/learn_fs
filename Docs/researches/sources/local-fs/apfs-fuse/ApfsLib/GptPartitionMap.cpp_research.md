# File Research: sources/local-fs/apfs-fuse/ApfsLib/GptPartitionMap.cpp

This implementation reads, verifies, lists, and searches GPT partition maps so apfs-fuse utilities can locate an APFS partition inside a whole-disk image/device. It defines packed GPT header and partition-entry structs locally, validates their expected sizes, and uses `Device` reads plus `Crc32` verification.

`LoadAndVerify()` reads the primary GPT header at one sector offset. It first assumes the device’s reported sector size, then retries with 4096-byte sectors if the EFI PART signature is not found. It validates signature, revision `0x00010000`, header size, and 128-byte partition entry size. It then zeroes the header CRC field in the in-memory header, computes CRC32 over the header, and verifies it against the stored header CRC.

After header validation, `LoadAndVerify()` reads the partition entry array, rounded up to the sector size, from `PartitionEntryLBA`, then verifies the partition array CRC. On success it stores stable pointers into `m_hdr_data` and `m_entry_data`; on failure it clears backing buffers and returns false.

`FindFirstAPFSPartition()` scans entries until an all-zero start/end entry and returns the first entry whose partition type GUID matches the hard-coded Apple APFS GPT type GUID. `GetPartitionOffsetAndSize()` converts a selected entry’s starting and ending LBAs into byte offset and byte length using `m_sector_size`. `ListEntries()` prints type GUID, unique GUID, LBA range, attributes, and the UTF-16 partition name as single-byte characters.

Notable risks: `GetPartitionOffsetAndSize()` does not bounds-check `partnum` against the loaded entry count. `ListEntries()` prints UTF-16 partition names by truncating each code unit to `char`, which is fine for ASCII names but not general Unicode. The header CRC calculation mutates `HeaderCRC32` in the buffer and does not restore it before storing `m_hdr`; this is harmless for current readers but means `m_hdr->HeaderCRC32` is zero after successful load.
