# File Research: sources/virtualization/qemu/block/dmg.h

Shared DMG driver header. `BDRVDMGState` contains the coroutine lock, chunk table arrays (`types`, `offsets`, `lengths`, `sectors`, `sectorcounts`), current cached chunk index, compressed/uncompressed buffers, and zlib stream.

It defines `BdrvDmgUncompressFunc` and declares the optional global function pointers `dmg_uncompress_bz2` and `dmg_uncompress_lzfse`, which are installed by the optional decompressor modules.
