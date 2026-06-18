# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa.h

This major public header defines the Storage Pool Allocator interface, core block-pointer/DVA layout, pool-level constants, config lock classes, async task flags, and a broad set of exported SPA/vdev/property/error/history APIs.

Core on-disk definitions:
- SPA block constants define supported block sizes, ashift range, config block size, DVA bit widths, compression/vdev bit widths, and the 128-byte `blkptr_t`.
- `dva_t` stores two opaque 64-bit DVA words; macros get/set ASIZE, GRID, VDEV, OFFSET, and GANG fields.
- `zio_cksum_salt_t` stores a 256-bit secret checksum/MAC salt.
- `blkptr_t` stores three DVAs, encoded block properties, padding, physical/logical birth TXGs, fill count, and 256-bit checksum.
- Extensive `BP_*` and `BPE_*` macros encode/decode normal, encrypted/authenticated, indirect-MAC, embedded, hole, gang, dedup, byteorder, fill, IV, size, and type/level fields.
- `SNPRINTF_BLKPTR()` formats block pointers for kernel, libzpool, and mdb callers.

SPA API surface:
- Pool lifecycle: open, rewind-open, create, import, tryimport, destroy, checkpoint, export, reset, stats.
- Async requests and task flags include config update, remove/probe/resilver, autoexpand, initialize/TRIM restarts, autotrim, and L2ARC rebuild.
- Vdev operations cover add/attach/detach/remove/initialize/TRIM/path/fru/split.
- Global spare and L2ARC device management APIs.
- Scan/scrub/resilver control and SPA sync entry points.
- Config cache generation/loading/update APIs, namespace lookup/add/remove/iteration, open refcount APIs, config locks, and vdev enter/exit locks.
- Accessors expose pool state, txgs, allocation classes, checkpoint/slop/dspace, features, roots, log state, import progress, event posting, error logging, waiters, and miscellaneous support routines.

Risk-sensitive invariants:
- Block-pointer bit layouts are on-disk format and shared across kernel, userland tools, and debuggers.
- Encrypted block pointers sacrifice the third DVA for salt/IV data and truncate fill to 32 bits.
- Embedded block pointers do not reference disk space and must use embedded-specific size/type macros.
- SPA config locks are divided into `SCL_*` classes; callers must use the correct lock class and rw mode.
- Many APIs are sync-context, config-lock, or transaction-context sensitive even though this header only declares them.
