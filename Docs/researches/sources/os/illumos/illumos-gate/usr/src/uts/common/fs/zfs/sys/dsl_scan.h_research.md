# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_scan.h

Read status: complete, 190 lines.

Purpose: scrub/resilver/deferred-free scan state and control interface.

Key structures and APIs:
- `dsl_scan_phys_t` is the on-disk resumable scan state; all members are `uint64_t` for byteswap, and it includes function/state, queue object, TXG bounds, current pass bounds, times, byte progress, errors, DDT class/bookmark, traversal bookmark, and flags.
- Flags include dataset revisit and scrub paused.
- `dsl_scan_t` stores in-memory scan state: pool, restart/done TXGs, sync timing, deferred-free mode, async destroy flags, sorted scan flags, checkpoint/suspend state, root zio/taskq, prefetch controls/queue, per-TXG stats, cached physical state, dataset queue, and pending bytes.
- APIs cover module init/fini, pool scan init/fini/sync, scan cancel/start, vdev assessment, scrub/resilver status and pause/resume, resilver restart, dataset instability, DDT entry scanning, dataset destroyed/snapshotted/clone-swapped notifications, active/paused checks, freed-block notification, scan IO queue destroy, and vdev transfer.

Important implementation constraints:
- Most persistent scan progress is on disk so scans can resume after reboot/panic.
- In-memory state controls suspension, checkpointing, sorted sequential scan behavior, prefetching, and deferred-free traversal.
- `DSL_SCAN_FLAGS_MASK` persists only selected flags.

Dependencies: ZFS context, ZIO, DDT, bplist, pool/dataset/dmu_tx forward declarations.

Research notes:
- Ties together scrub, resilver, async destroy, DDT scanning, and deferred free handling.
