# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatdata.h

This header declares FastFAT global state, tuning constants, time conversion helpers, debug tracing macros, and debug-only break controls used across the driver.

Main declarations:
- Global filesystem data:
  - `FatData`
  - `FatGarbageIosb`
  - filesystem device objects
  - fast I/O dispatch table
  - disk accounting state
- Memory/synchronization globals:
  - IRP context, nonpaged FCB, and ERESOURCE lookaside lists.
  - close-context SList.
  - close queue mutex.
  - reserve MDL and reserve event.
- Time constants:
  - zero/max large integers.
  - small relative timeouts.
  - day and FAT epoch constants.
  - `FatTimeJanOne1980`.
  - magic divisors for fast conversion from 100ns units to milliseconds and milliseconds to days.
- Operational tuning:
  - `READ_AHEAD_GRANULARITY`
  - `FAT_MAX_IO_RUNS_ON_STACK`
  - `FAT_MAX_DELAYED_CLOSES`
  - `FAT_DEFAULT_DEFRAG_CHUNK_IN_BYTES`
  - close-count limit declaration.
- Time rounding constants:
  - 10ms and 2s rounding helpers.
  - `HighPartPerDay`.

Debug infrastructure:
- Under `FASTFATDBG`, it defines trace categories for each major subsystem: cleanup, close, create, directory control, EA, file info, fsctl, lock control, read/write, volume info, flush, device control, shutdown, PNP, allocation, directory support, cache support, device I/O support, FSP dispatcher, and others.
- `DebugTrace` prints thread id, indentation, and formatted messages when a trace level is enabled.
- `DebugDump` optionally dumps structures and asserts.
- `DebugUnwind` traces abnormal termination.
- `TimerStart`/`TimerStop` accumulate lightweight performance counters.
- Retail builds reduce these macros to no-ops.
- `DbgDoit` remains available for general `DBG` builds.
- Debug break controls expose statuses of interest for exception and IRP completion breakpoints.

Role in the subset:
- This header is the cross-file declaration point for FastFAT’s driver-wide state and diagnostics. It supports the implementation files in this group: `fatinit.c` initializes many of these globals, while `fatdata.c` defines and uses them.
