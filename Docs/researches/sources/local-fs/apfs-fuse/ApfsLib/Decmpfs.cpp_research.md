# File Research: sources/local-fs/apfs-fuse/ApfsLib/Decmpfs.cpp

This file implements APFS/HFS-style `com.apple.decmpfs` compressed-file expansion. It supports algorithms 3/4 zlib, 7/8 LZVN, 9/10 uncompressed, 11/12 LZFSE, and 13/14 LZBITMAP, with even-numbered variants stored in the resource fork.

`IsDecompAlgoSupported()` and `IsDecompAlgoInRsrc()` classify algorithm IDs. `DecompressFile()` validates the compression header, logs algorithm details when debug is enabled, and either decodes inline attribute data or reads `com.apple.ResourceFork` through `ApfsDir`.

Resource-fork zlib mode parses a resource fork header and `CmpfRsrc` entries. Other resource-fork modes use an offset list of 64 KiB chunks. Inline modes decode directly from xattr payload after `CompressionHeader`.

It uses decompression helpers from `Util.h`: zlib, LZVN, LZFSE, and LZBITMAP. It also handles uncompressed marker bytes for several formats.

Notable risks: many format assumptions are enforced with `assert()` or comments like “Assuming”. Bounds checks exist for some chunk sizes but not every pointer derived from resource-fork offsets.
