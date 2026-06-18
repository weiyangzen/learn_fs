# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dumpsubr.c

## Purpose

Implements illumos kernel crash dump setup and dump execution. It owns dump device configuration, dump header construction, page selection, page-to-PFN mapping metadata, compressed page streaming, panic/live dump helper coordination, and uncompressed trailer regions for stack summary, FMA ereports, and console messages.

## Main Responsibilities

- Maintains global dump configuration: `dumpvp`, `dumpvp_size`, `dumppath`, `dumphdr`, `dump_conflags`, `dumpbuf`, and `dumpcfg`.
- Initializes and tears down dump devices with `dumpinit()` and `dumpfini()`.
- Writes buffered dump data through `dumpvp_write()` and `dumpvp_flush()`, using `VOP_DUMP()` during panic and `vn_rdwr()` during live dump.
- Builds dump maps with `dump_addpage()`, `dump_page()`, `dump_as()`, and `dump_process()`.
- Runs `dumpsys()` to emit symbol tables, VA-to-PFN maps, PFN tables, compressed memory data, platform data, metrics, and leading/trailing dump headers.
- Supports single-threaded lzjb, parallel lzjb, and panic-time parallel bzip2 compression.
- Saves uncompressed summary, ereport, and message sections via `dump_summary()`, `dump_ereports()`, and `dump_messages()`.

## Key Data Structures

- `dumpcfg_t`: persistent compression/helper configuration, including helpers, buffers, bitmaps, spare-memory reservations, helper CPU bitmap, and panic helper lock state.
- `dumpbuf_t`: single buffered writer state for dump device offsets and aligned I/O.
- `dumpsync_t`: per-dump runtime counters, queues, progress, timing, and live/panic mode.
- `helper_t`: per-compression-stream state, including input/output buffers, lzjb page buffers, bzip2 stream state, metrics, and helper identity.
- `cbuf_t` and `cqueue_t`: stateful buffer descriptors and queue primitives used between master, helper, free-buffer, and writer paths.
- `dumpmlw_t`: physical memory list walker optimized for sequential bitnum-to-PFN lookup.

## Important Control Flow

- `dumphdr_init()` lazily allocates the dump header, dump I/O buffer, PID list, helper CPU bitmap, stack scratch buffer, UUID, and PFN bitmaps sized from physical memory.
- `dump_update_clevel()` chooses compression level from CPU count, platform threshold, and dump device I/O size; allocates minimum helpers/buffers and reserves virtual address space for best-case panic-time expansion.
- `dumpsys_get_maxmem()` runs only at panic dump time. It searches pages not selected for dumping, first in `CBUF_MAPSIZE` ranges and then as individual pages, maps them into reserved VM, marks them as dump-owned, and uses them to enable more helpers/output buffers/bzip2 state.
- `dumpsys()` is the top-level dump sequence:
  - determines dump offset and content mode,
  - writes kernel symbols,
  - walks kernel and optionally process address spaces,
  - writes PFN table,
  - starts live taskq helpers or panic idle-CPU helpers,
  - runs `dumpsys_main_task()`,
  - writes compression metadata and dump headers,
  - writes panic-only summary/ereport/message trailers.
- `dumpsys_main_task()` maps selected PFN ranges, dispatches them to helpers or compresses serially, drains write/error queues, unmaps ranges, updates progress, and closes helper queues at EOF or I/O error.
- `dumpsys_helper()` is entered by panic-idle CPUs. It claims a `FREEHELPER`, records CPU participation in `helpermap`, runs lzjb or bzip2 compression, and marks completion.
- `dumpsys_live_helper()` performs the same compression path from taskq context for live dumps.

## Compression and Stream Format Notes

- Compression level meanings:
  - `0`: serial lzjb, no helper stream format.
  - `DUMP_CLEVEL_LZJB`: parallel lzjb streams.
  - `DUMP_CLEVEL_BZIP2`: parallel bzip2 streams.
- Parallel streams are tagged with helper-specific stream tags so multiple helper outputs can be interleaved.
- `dumpsys_lzjbrun()` writes stream blocks containing a tagged block-size word followed by stream headers or per-page compressed records.
- `dumpsys_bzrun()` feeds page data and stream headers into the bzip2 stream and writes tagged compressed blocks.
- Live dumps downgrade bzip2 to lzjb because the panic-only spare-memory path is not used.

## Concurrency and Panic Constraints

- Panic helpers cannot rely on normal blocking kernel services, so panic queues use custom spin locks and atomic state; live dumps use mutexes and condition variables.
- `cqueue_t` producer counts let consumers distinguish “temporarily empty” from “closed and done.”
- `dump_pagecopy()` uses `on_trap()` to tolerate data access/ECC faults while copying pages and substitutes sentinel words for bad memory.
- `dump_timeleft` is refreshed throughout long-running loops to avoid dump timeout expiration.
- `dump_check_used` is enabled when dumpsys borrows pages so allocator paths can avoid dump-owned memory.

## External Interfaces and Dependencies

- Exports dump control and support functions including `dumpinit()`, `dumpfini()`, `dumpsys()`, `dump_resize()`, `dumpvp_resize()`, `dump_set_uuid()`, `dump_get_uuid()`, `dump_page()`, `dump_addpage()`, `dumpvp_write()`, `dumpsys_helper()`, and `dumpsys_helper_nw()`.
- Depends on VM/HAT page mapping, vnode/block-device dump operations, ksyms, lzjb `compress()`, bzip2, FMA ereport dumping, error queues, logging queues, platform dump hooks, and panic state.

## Notable Edge Cases

- Avoids block-device dump use when the device is mounted or is a ZFS swap zvol.
- For zvol dump devices, invokes `DKIOCDUMPINIT`/`DKIOCDUMPFINI`.
- Reserves first device page and special trailer regions; swap dump starts one-fifth into the device.
- Clears `DF_COMPLETE` if I/O failed or fewer pages were written than expected.
- `dump_set_uuid()` accepts exactly canonical 36-character UUID strings and only permits setting once.
