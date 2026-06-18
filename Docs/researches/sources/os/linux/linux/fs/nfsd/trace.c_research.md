# File Research: sources/os/linux/linux/fs/nfsd/trace.c

## Summary
Instantiates NFSD tracepoints by defining `CREATE_TRACE_POINTS` before including `trace.h`.

## Main Responsibilities
- Provides the single compilation unit that emits storage and definitions for tracepoints declared in `fs/nfsd/trace.h`.

## Key Data Structures and Interfaces
- `CREATE_TRACE_POINTS` controls Linux tracepoint definition generation.
- `#include "trace.h"` imports the NFSD trace event declarations.

## Important Behavior
This file intentionally contains no runtime logic beyond tracepoint instantiation.

## Dependencies
Depends on NFSD `trace.h` and the kernel tracepoint macro system.

## Risks and Subtleties
Only one translation unit should define `CREATE_TRACE_POINTS` for a trace header. Duplicating this pattern elsewhere would cause duplicate tracepoint definitions at link time.
