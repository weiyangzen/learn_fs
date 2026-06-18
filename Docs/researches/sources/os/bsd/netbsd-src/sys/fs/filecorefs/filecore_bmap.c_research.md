# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_bmap.c

Read completely: 270 lines.

Implements FileCore logical-to-physical block mapping and related read helpers. `filecore_bmap()` supplies the underlying device vnode, computes a conservative readahead run length, and maps a file logical block through `filecore_map()` using the file’s directory-entry address.

`filecore_map()` decodes FileCore fragment and sector addressing, identifies the map zone, reads map sectors, scans variable-length allocation runs encoded in bit fields, and translates a logical block within a fragment to a physical device block. It wraps through zones and returns `E2BIG` if no matching allocation run is found.

`filecore_bread()` maps a FileCore address to its first physical block and reads a requested size from the device. `filecore_dbread()` caches the mapped first block for a directory node and reads the fixed 2048-byte directory body.
