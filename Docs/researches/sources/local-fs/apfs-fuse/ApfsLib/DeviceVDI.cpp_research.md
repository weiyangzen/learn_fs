# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceVDI.cpp

`DeviceVDI` implements a minimal VirtualBox VDI reader. It parses the preheader and version 1+ header, validates signature `0xBEDA107F` and version `0x00010001`, extracts disk size, block size, total block count, data offset, and block map.

`Read()` splits reads across VDI blocks, maps logical block numbers through the block map, zero-fills unallocated blocks (`0xFFFFFFFF`), and reads allocated blocks from `data_offset + map_entry * block_size + block_offs`.

The implementation uses C `FILE*` I/O and `fopen_s`, which is MSVC-oriented and may need portability support elsewhere.

Notable risks: block number is computed as `offs >> 20`, assuming 1 MiB blocks even though `m_block_size` is read from the VDI header. There are no bounds checks for `block_nr` against `m_block_map`.
