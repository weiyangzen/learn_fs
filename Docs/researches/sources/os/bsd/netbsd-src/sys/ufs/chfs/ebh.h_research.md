# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh.h

This is the public/internal CHFS eraseblock handler header. It defines in-memory eraseblock header wrappers, scan structures, eraseblock state structures, operation tables, the main `chfs_ebh` descriptor, and the public EBH API.

Key definitions:
- `struct chfs_eb_hdr`: combines common erase-counter header with either NOR or NAND header.
- LEB status enum: unmapped, mapped, dirty, invalid, erase, erased, free.
- EB header status enum: OK, dirty, invalidated, bad magic, bad CRC, free, no header.
- `struct chfs_ltree_entry`: per-logical-eraseblock RB tree entry with user count and rwlock.
- `struct chfs_scan_leb` / `struct chfs_scan_info`: temporary scan results grouped into queues and a used RB tree.
- `struct chfs_peb`: physical eraseblock metadata used in free/in-use trees and erase queues.
- `struct chfs_ebh_ops`: flash-type-specific operations for header I/O, validation, recovery, creation, and data offset calculation.
- `struct chfs_ebh`: the runtime eraseblock handler descriptor, including flash device/interface, maps, locks, queues, trees, background erase thread, and NAND max serial.

Public API:
- Open/close: `ebh_open`, `ebh_close`.
- I/O: `ebh_read_leb`, `ebh_write_leb`, `ebh_change_leb`.
- Mapping lifecycle: `ebh_map_leb`, `ebh_unmap_leb`, `ebh_erase_leb`, `ebh_is_mapped`.

Dependencies:
- Kernel-only includes for NetBSD types, trees, queues, locks, kmem, kthread, and flash interface.
- Always includes `ebh_media.h` for on-media header structures.

Design notes:
- `chfs_ebh_ops` abstracts NOR/NAND differences while keeping shared scan, lock, and wear-leveling logic in `ebh.c`.
- `max_serial` is meaningful only for NAND.
- `layout_map` and an older mutex field are commented out, indicating unfinished or abandoned layout-level logic.
