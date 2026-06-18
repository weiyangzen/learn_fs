# sources/storage-engines/foundationdb/fdbrpc/TraceFileIO.cpp

## Purpose
`TraceFileIO.cpp` provides optional debug-only tracking of file writes, reads, and truncates for a named file. In normal builds it compiles to no-op functions.

## Important APIs, Types, and Functions
The externally relevant functions are `debugFileCheck`, `debugFileSet`, and `debugFileTruncate`. When enabled, helpers include `debugFileSetup`, `debugFileTrim`, and `debugFileIsSet`, plus global maps for tracked data, masks, and regions.

## Control Flow
With `CENABLED(0, NOT_IN_CLEAN)` enabled, setup allocates memory for configured file regions and a page-sized all-ones mask. `debugFileSet` copies overlapping written bytes into the in-memory region and marks the mask. `debugFileCheck` compares a read buffer with fully or partially known bytes and emits warning trace events on mismatch. `debugFileTruncate` clears mask bytes after the truncation point. The compiled default path defines empty functions.

## State and Persistence Behavior
Enabled mode holds global heap buffers keyed by file-region offset and tracks only the hard-coded `debugFileName`. It does not write persistent diagnostics; it emits `TraceEvent`s. Default mode has no state.

## Dependencies and Integration Points
It depends on `fdbrpc/TraceFileIO.h` and Flow trace/assert utilities through included headers. `AsyncFileNonDurable` calls these hooks around simulated writes, reads, and truncates.

## Risks and Edge Cases
The enabled branch allocates large buffers and never frees them. It is manually configured by editing globals, so it is easy to track the wrong file or region. It is not thread-safe and uses assertions for internal assumptions. The disabled default can hide accidental dependence on these functions because all calls become no-ops.

## Test Signals
There are no direct unit tests here. Signals are trace events such as `DebugFileFail`, `DebugFileUnsetCheck`, and `DebugFileSkipping*` when a developer enables the debug branch and runs file I/O simulations.
