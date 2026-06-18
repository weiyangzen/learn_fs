# File Research: sources/local-fs/xfsprogs/db/io.c

## Purpose
Implements xfs_db's current-location stack, implicit navigation ring, buffer reads/writes, device selection, CRC/write helpers, and type retagging.

## Main Interfaces
- Registers `pop`, `push`, `stack`, `forward`, `back`, and `ring` through `io_init()`.
- Exports global cursor stack state `iocur_base`, `iocur_top`, `iocur_sp`, and `iocur_len`.
- Exports cursor operations `push_cur()`, `pop_cur()`, `off_cur()`, `set_cur()`, `set_log_cur()`, `set_rt_cur()`, `set_iocur_type()`, `write_cur()`, `ring_add()`, and `print_iocur()`.
- Exports verifier helpers `xfs_dummy_verify()` and `xfs_verify_recalc_crc()`.

## Control Flow
The explicit stack stores current type, buffer, offsets, inode context, directory inode, mode, buffer map, and CRC flags. `set_cur()` and variants replace the top cursor by reading a buffer from the data, log, or realtime device with salvage mode; discontiguous maps are supported for fragmented metadata. The ring keeps the last 20 navigation targets and supports back/forward movement. `write_cur()` recalculates inode or dquot CRCs when applicable, writes the buffer, then re-reads it from disk.

## Dependencies
Uses libxfs buffer IO, type descriptors and verifier ops, inode/dquot CRC helpers, allocation wrappers, field sizing, and global mount/device state.

## Risks And Invariants
- `__set_cur()` uses salvage reads so verifier-detected corrupt metadata can still be inspected.
- Ring entries shallow-copy cursor structs; mapped buffers are re-read when revisiting.
- `set_log_cur()` requires an external log device; `set_rt_cur()` requires a loaded realtime device.
- `set_iocur_type()` special-cases inodes to route through `set_cur_inode()` so the entire inode cluster is verified consistently.
