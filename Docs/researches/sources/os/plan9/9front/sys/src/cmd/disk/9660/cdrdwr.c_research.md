# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/cdrdwr.c

Core ISO image open/create, descriptor parsing, endian conversion, and buffered read/write primitives.

Key behavior:
- `createcd` creates a new image, writes initial empty sectors, primary descriptor, optional boot/Joliet/dump structures, descriptor terminator, and initializes `nextblock`.
- `opencd` opens an existing block-aligned image, parses descriptors, detects Plan 9/Rock Ridge/conform/boot/Joliet/dump features, and validates the system identifier.
- `big` and `little` decode multi-byte integers.
- `Creadblock` performs block-addressed reads after flushing pending writes.
- `parsedir` converts on-disc directory records into `Direc`, including Plan 9 system-use fields when applicable.
- `setroot`, `setvolsize`, and `setpathtable` patch descriptor fields after layout is known.
- `Cput*`, `Cread`, `Cwseek`, `Crseek`, and related helpers abstract byte, endian, string, UTF-16-ish rune, block-padding, and date emission.

Notable dependencies:
- `Cputisopvd`, `Cputjolietsvd`, `Cputendvd`, dump and boot helpers.
- Plan 9 `Biobuf` for separate read/write streams on the same image.

Research notes:
- The implementation maintains separate read and write buffers and carefully flushes the opposite side when switching directions.
- `parsedir` has a comment noting Rock Ridge parsing is not implemented.
- `Cputc` contains a suspicious leftover debug conditional around offset `0x9962` and `abort()` for byte values >=256.
