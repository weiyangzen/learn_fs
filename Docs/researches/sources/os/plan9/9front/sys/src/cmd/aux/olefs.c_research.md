# File Research: sources/os/plan9/9front/sys/src/cmd/aux/olefs.c

`olefs` exposes Microsoft OLE Compound File streams as a read-only 9P filesystem, mounted by default at `/mnt/doc`. It parses the 512-byte OLE header, FAT/depot block maps, root directory chain, and small-stream storage.

The in-memory `Ofile` holds the BIFF/OLE block map, root block, small-block root, and input `Biobuf`. `Odir` represents directory entries with UTF-16 names, type, tree links, stream start, and stream size.

Reads follow FAT chains for large streams and use the root small-block depot for streams under 0x1000 bytes. Directory entries are traversed as a binary tree with recursive child directories. Names are sanitized by converting spaces to U+2423 and control/slash/problem bytes to `:`.

The 9P service implements read-only file reads via `oleread`; directories and files are created in an in-memory tree using lib9p. It detects the OLE magic header and rejects bad magic.

Caveats: no full cycle detection beyond a recursion depth cap of 100; timestamps are ignored; malformed FAT/depot structures mostly fail with fatal errors or nil open.
