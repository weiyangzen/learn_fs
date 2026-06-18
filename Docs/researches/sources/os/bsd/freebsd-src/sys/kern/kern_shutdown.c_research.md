# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_shutdown.c

## Purpose

Implements FreeBSD kernel shutdown, reboot, panic, reroot, and kernel crash dump support. This file is the central path from user/kernel initiated reboot requests through filesystem sync, shutdown event handlers, optional panic dump generation, final halt/power/reset behavior, and dumper configuration.

## Main Responsibilities

- Handles `reboot(2)` through `sys_reboot()`, privilege/MAC checks, and either `kern_reboot()` or `kern_reroot()`.
- Implements `shutdown_nice()` by signaling `init(8)` with shutdown intent-specific signals.
- Coordinates shutdown phases:
  - `shutdown_pre_sync`
  - filesystem sync via `bufshutdown()`
  - `shutdown_post_sync`
  - optional crash dump
  - `shutdown_final`
  - CPU reset fallback
- Implements panic handling via `panic()` and `vpanic()`, including recursive panic behavior, KDB/debugger hooks, panic tracing, optional sync suppression, and panic reboot/poweroff policy.
- Manages kernel dump devices through `dumper_create()`, `dumper_insert()`, `dumper_remove()`, `dumper_destroy()`, and `kern.shutdown.dumpdevname`.
- Supports encrypted kernel dumps under `EKCD`, with AES-256-CBC and ChaCha20 setup.
- Supports compressed dumps via the kernel compressor interface, including gzip/zstd format selection and residual block handling.
- Provides dump write lifecycle helpers: `dump_start()`, `dump_append()`, `dump_write()`, `dump_finish()`, and `dump_init_header()`.
- Implements `RB_REROOT` support for remounting a new root filesystem while preserving selected mounts.

## Important Control Flow

- `kern_reboot()` is the primary shutdown pipeline. It drops Giant if necessary, binds to CPU 0 on SMP, marks `rebooting`, invokes shutdown handlers, syncs buffers unless `RB_NOSYNC`, optionally dumps core, and finally invokes reset handlers.
- `vpanic()` stops other CPUs where possible, marks `scheduler_stopped`, sets `panicstr`, emits panic diagnostics, enters KDB depending on tunables, sets dump/sync/power policy bits, and calls `kern_reboot()`.
- `doadump()` serializes dump attempts with `dumping`, saves CPU context, and iterates registered dumpers until one succeeds.
- `dump_start()` computes dump layout near the end of the dump device, preserving leading metadata and reserving space for headers and optional encrypted dump key.
- `dump_finish()` flushes compression, patches dump length/parity when compressed, writes headers, and finalizes the device with a zero-length write.

## State, Tunables, and Locking

- Global shutdown/panic state includes `panicstr`, `scheduler_stopped`, `dumping`, `rebooting`, and `dumped_core`.
- Dumper list `dumper_configs` is protected by `dumpconf_list_lk`.
- Key tunables include `kern.panic_reboot_wait_time`, `kern.reboot_wait_time`, `kern.sync_on_panic`, `kern.poweroff_on_panic`, `kern.powercycle_on_panic`, `debug.debugger_on_panic`, and `kern.shutdown.poweroff_delay`.
- Shutdown ordering is eventhandler based; priority registration matters for final halt/panic/poweroff behavior.
- Dump writes enforce block alignment, device bounds, and media offset/size constraints in `dump_check_bounds()`.

## Filesystem Relevance

This file directly affects filesystem integrity at shutdown. The normal reboot path invokes `bufshutdown()` unless explicitly bypassed, while panic paths commonly set `RB_NOSYNC` unless `sync_on_panic` is enabled. The reroot path manipulates mount lists, preserves `/dev`, unmounts all other filesystems, remounts root, and updates directory references through `mountcheckdirs()`.

## Cautions

- Panic and shutdown paths run under degraded conditions; many operations are deliberately best-effort.
- Recursive panic paths suppress sync and may enter debugger conditionally.
- Compressed dumps may shrink effective dump extent dynamically but still rely on later bounds checks.
- AES-CBC encryption cannot be combined with compression because compressed output may not be block-aligned.
