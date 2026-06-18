# File Research: sources/os/linux/linux-stable/fs/lockd/trace.c

## Summary
Tracepoint instantiation unit for lockd.

## Behavior
Defines `CREATE_TRACE_POINTS` and includes `trace.h`, causing the trace event declarations in the header to emit storage and registration code in exactly one translation unit.

## Dependencies
Linux tracepoint build conventions and `fs/lockd/trace.h`.

## Risks
This file must remain minimal; adding other includes before trace definitions can affect tracepoint generation.
