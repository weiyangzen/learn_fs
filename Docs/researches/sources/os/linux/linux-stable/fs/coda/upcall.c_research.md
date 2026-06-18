# File Research: sources/os/linux/linux-stable/fs/coda/upcall.c

This file implements Coda upcalls from the kernel to Venus and downcalls from Venus back to the kernel.

Key responsibilities:
- Provides Venus RPC wrappers for root fid, getattr, setattr, lookup, open/close, create, mkdir, remove, rmdir, rename, link, symlink, fsync, access, pioctl, statfs, and access-intent notifications.
- Implements `coda_upcall()`, the central request queueing and reply-wait mechanism.
- Implements `coda_downcall()` for Venus-initiated cache invalidation and fid replacement.
- Handles interrupt and timeout behavior for synchronous upcalls.

Important control flow:
- `alloc_upcall()` allocates and initializes a request header with opcode, pid, pgid, and fsuid in the initial namespaces.
- Each `venus_*()` wrapper builds a specific `union inputArgs` packet, embeds names at offsets when needed, calls `coda_upcall()`, copies output values, and frees the request buffer.
- `venus_access_intent()` may issue asynchronous finalizer calls by passing `outSize == NULL`.
- `coda_upcall()`:
  - Requires `vc_inuse`.
  - Allocates `struct upc_req`, assigns a unique sequence number, appends it to `vc_pending`, and wakes Venus.
  - Returns immediately for async requests.
  - Waits for synchronous replies via `coda_waitfor_upcall()`.
  - Maps positive Venus result codes to negative kernel errno.
  - If interrupted after Venus read the request, sends an async `CODA_SIGNAL` request.
- `coda_downcall()` validates message size by opcode, locates the mounted superblock, resolves affected fids to inodes, and applies Coda cache/dcache invalidation semantics.

Dependencies:
- Queue endpoints are consumed by `psdev.c`.
- Cache invalidation depends on `coda_cache_clear_all()`, `coda_flag_inode()`, `coda_flag_inode_children()`, `coda_replace_fid()`, and dcache pruning helpers.
- Uses Coda wire structs and opcodes from `<linux/coda.h>`.

Risks and invariants:
- Certain opcodes such as close/store/access-intent/release are made effectively uninterruptible until Venus reads them, avoiding reference-count or data-loss problems.
- Name-bearing upcalls manually pack NUL-terminated names into variable-size request buffers; length calculations and word-boundary padding are central correctness points.
- `venus_pioctl()` validates in/out sizes against `VC_MAXDATASIZE` and validates returned offset/length before copying to userspace.
- Downcalls intentionally split global flushes, per-user purges, directory zaps, file zaps, fid purges, and fid replacement semantics.
