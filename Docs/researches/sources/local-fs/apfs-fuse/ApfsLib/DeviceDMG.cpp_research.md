# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceDMG.cpp

`DeviceDMG` implements a read-only device adapter for Apple DMG images. It wraps `DiskImageFile`, which may decrypt encrypted DMGs, then parses the trailing `koly` header and block-run metadata.

If no `koly` signature is found, it treats the file as raw. For normal DMG, it uses XML plist metadata, finds `resource-fork/blkx` arrays, extracts `mish` data blobs, and converts `MishEntry` runs into `DmgSection` records.

`Read()` binary-searches the section containing the requested logical byte offset, reads raw sections directly, zero-fills ignored sections, and decompresses ADC, zlib, bzip2, or LZFSE sections. With `DMG_CACHE` enabled, it caches one decompressed compressed section globally.

`ProcessHeaderRsrc()` is unimplemented and returns false, so legacy resource-fork-only DMGs are unsupported. `ProcessMish()` skips terminator/special methods `0xFFFFFFFF` and `0x7FFFFFFE`.

Notable risks: decompressor return lengths are not validated in all paths, section ordering is assumed for binary search, and large compressed sections can allocate full uncompressed section buffers.
