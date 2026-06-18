# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh.c

This is the CHFS eraseblock handler implementation. It provides the logical eraseblock API declared in `ebh.h`, owns LEB-to-PEB mapping state, implements NOR/NAND-specific eraseblock header formats, scans flash on open, maintains free/in-use/erase queues, and runs a background erase thread.

Key responsibilities:
- Flash header protocol: `nor_*` and `nand_*` functions create, read, validate, write, dirty-mark, invalidate, and free eraseblock headers.
- Logical block locking: an RB tree of `chfs_ltree_entry` objects gives per-LEB reader/writer locking with reference-counted tree entries.
- Wear-leveling state: free PEBs are ordered by erase count, in-use PEBs by physical number, and erase candidates are kept in TAILQs.
- Media scan/recovery: `chfs_scan`, `nor_process_eb`, and `nand_process_eb` classify PEBs into corrupted, free, erased, erase-needed, and used sets.
- Public operations: `ebh_open`, `ebh_close`, `ebh_read_leb`, `ebh_write_leb`, `ebh_erase_leb`, `ebh_map_leb`, `ebh_unmap_leb`, `ebh_is_mapped`, and `ebh_change_leb`.

Important behavior:
- NOR headers use a dirty bit in the logical ID and can invalidate old headers by zeroing CRC/LID. During atomic change, the old NOR header is first marked dirty, then the new PEB is written, then the old header is invalidated.
- NAND headers use a monotonically increasing serial number. Recovery chooses the higher serial when multiple PEBs reference the same LEB.
- `get_peb` takes the lowest-erase-count free PEB, or synchronously erases queued PEBs if no free PEB is available.
- `erase_thread` waits on `eth_wakeup` and processes `to_erase`/`fully_erased` queues via `free_peb`.
- Unmapped LEB reads return a buffer filled with `0xff`.

Dependencies:
- NetBSD flash API: `flash_read`, `flash_write`, `flash_erase`, `flash_block_isbad`, `flash_block_markbad`, `flash_get_device`, `flash_get_interface`, `flash_get_size`.
- CHFS helpers/macros from `ebh.h`, `ebh_media.h`, `ebh_misc.h`, and `debug.h`.
- Kernel RB tree, TAILQ, mutex, rwlock, condvar, kthread, and kmem APIs.

Notable implementation risks:
- Several paths assume valid `lnr` indices into `ebh->lmap`; bounds are enforced mainly by callers or assertions.
- `ebh_close` frees `ebh` itself, so callers must not use or separately free the descriptor after closing.
- `ebh_open` also frees `ebh` on scan failure, which is unusual for an initializer taking caller-supplied storage.
- `release_peb` removes a PEB from the in-use tree but does not free the removed tree object there; ownership is easy to misread because erase queue entries are separately allocated.
- `erase_callback` requeues failed erases without consistently taking `erase_lock` in the non-DONE branch.
- `ebh_change_leb` calls `find_peb_in_use` without holding `erase_lock`, then calls `release_peb`, and later frees `peb`; this is a sensitive ownership/locking area.
