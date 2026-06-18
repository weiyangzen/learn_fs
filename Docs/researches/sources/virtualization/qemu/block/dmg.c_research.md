# File Research: sources/virtualization/qemu/block/dmg.c

Implements QEMU's read-only Apple DMG/UDIF image format driver. It supports zero, raw, ignored, zlib, optional bzip2, and optional LZFSE chunk types. It probes weakly by `.dmg` filename suffix.

Open flow applies auto read-only, opens the file child, loads optional `dmg-bz2` and `dmg-lzfse` modules, locates the `koly` trailer near EOF, validates data/resource/plist offsets against the trailer location, reads total sectors, then parses either the resource fork or XML property list to build chunk tables. MISH block parsing recognizes chunk entries, ignores comments/end markers, warns for unsupported types, validates sector counts and compressed lengths with 64 MiB caps, and records per-chunk type, file offset, compressed length, guest sector start, and sector count. It also tracks maximum compressed and uncompressed chunk sizes for buffer allocation.

Runtime reads are 512-byte aligned and serialized by a coroutine mutex. `dmg_read_chunk()` binary-searches the chunk containing a sector, lazily decompresses or reads the whole chunk into a single cached buffer, and handles zero/ignore chunks specially without large zero buffers. Zlib chunks use the file's persistent zstream; bzip2/LZFSE chunks call optional function pointers; raw chunks read directly. `dmg_co_preadv()` copies requested sectors from the current chunk buffer or zero-fills them.

Close frees all chunk arrays, aligned buffers, and the zlib stream. The driver registers as format `dmg`, with default child permissions, 512-byte request alignment, and read-only semantics.
