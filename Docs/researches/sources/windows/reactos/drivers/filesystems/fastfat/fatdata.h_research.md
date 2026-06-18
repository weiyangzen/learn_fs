# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatdata.h

## Purpose

`fatdata.h` declares global FastFAT driver data and debug/timing macros shared across the driver. It is the header counterpart to `fatdata.c`.

## Global Declarations

The header declares:

- `extern FAT_DATA FatData`
- `FatGarbageIosb`
- lookaside lists:
  - `FatIrpContextLookasideList`
  - `FatNonPagedFcbLookasideList`
  - `FatEResourceLookasideList`
- close queue state:
  - `FatCloseContextSList`
  - `FatCloseQueueMutex`
- filesystem device objects:
  - `FatDiskFileSystemDeviceObject`
  - `FatCdromFileSystemDeviceObject`
- time and arithmetic constants:
  - `FatLargeZero`
  - `FatMaxLarge`
  - `Fat30Milliseconds`
  - `Fat100Milliseconds`
  - `FatOneSecond`
  - `FatOneDay`
  - `FatJanOne1980`
  - `FatDecThirtyOne1979`
  - `FatTimeJanOne1980`
  - `FatMagic10000`
  - `FatMagic86400000`
- reserve MDL/event:
  - `FatReserveMdl`
  - `FatReserveEvent`
- `FatFastIoDispatch`
- `FatDiskAccountingEnabled`

## Time Conversion Macros

- `FatConvert100nsToMilliseconds`
- `FatConvertMillisecondsToDays`
- `FatConvertDaysToMilliseconds`

These use `RtlExtendedMagicDivide` and predefined magic divisors/shifts for fast time conversion.

## I/O and Close Constants

- `READ_AHEAD_GRANULARITY` is `0x10000`.
- `FAT_MAX_IO_RUNS_ON_STACK` is 5.
- `FAT_MAX_DELAYED_CLOSES` is 16.
- `FatMaxDelayedCloseCount` is declared.
- `FAT_DEFAULT_DEFRAG_CHUNK_IN_BYTES` is `0x10000`.

## Time Rounding Constants

Defines:

- `TenMSec`
- `TwoSeconds`
- `AlmostTenMSec`
- `AlmostTwoSeconds`
- `HighPartPerDay`

These support FAT timestamp rounding/conversion behavior elsewhere.

## Debug Trace Infrastructure

Under `FASTFATDBG`, the header defines trace-level bit flags for major subsystems:

- errors, debug hooks, exceptions, unwind
- cleanup, close, create, directory control
- EA, file info, FS control, locks
- read/write/flush/volume info
- device control, shutdown, PNP
- support modules such as allocation, directory, cache, verify, device I/O, structure support
- FSP dispatcher/dump

It declares:

- `FatDebugTraceLevel`
- `FatDebugTraceIndent`
- FSD/FSP/I/O counters
- `FatTotalTicks`
- `FatPerformanceTimerLevel`
- `FatNull`

Macros:

- `DebugTrace`
  - checks trace mask
  - prints thread id and indentation
  - adjusts indentation before/after printing
- `DebugDump`
  - prints text and optionally dumps a FastFAT structure with `FatDump`
  - asserts afterward
  - has MSVC and non-MSVC variants
- `DebugUnwind`
  - reports abnormal SEH termination
- `DebugDoit`
  - executes debug-only statements
- `TimerStart` / `TimerStop`
  - collect performance-counter elapsed ticks by trace level

Without `FASTFATDBG`, these macros become no-ops and `FatNull` is `NULL`.

## DBG-Only Support

Under `DBG`, the header declares:

- `FatBreakOnInterestingIoCompletion`
- `FatBreakOnInterestingExceptionStatus`
- `FatBreakOnInterestingIrpCompletion`
- `FatTestRaisedStatus`

It also defines `DbgDoit` as enabled only for DBG builds.

## Integration

This header is included broadly through `fatprocs.h`. It connects:

- debug dump support in `dumpsup.c`
- globals implemented in `fatdata.c`
- exception tracing and completion diagnostics throughout FastFAT
- timing and conversion helpers used by timestamp code
