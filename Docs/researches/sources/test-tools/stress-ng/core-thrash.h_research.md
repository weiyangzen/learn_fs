# sources/test-tools/stress-ng/core-thrash.h

## Purpose
`core-thrash.h` exposes the background memory-thrashing lifecycle API.

## Important APIs, Types, And Functions
It declares `stress_thrash_start` and `stress_thrash_stop`. The start function returns a status code, while stop performs helper teardown.

## Control Flow
Callers start the thrash helper before or during a stressor run and call stop during cleanup. Unsupported builds still provide the same API through stub implementations in `core-thrash.c`.

## State And Persistence
No state is defined in the header. Implementation state is process-local helper PID and signal state, with possible system VM side effects while active.

## Dependencies And Integration Points
The header is included by stressors or core orchestration code that honors `--thrash`. It relies on common stress-ng declarations included before or through implementation files.

## Risks
Callers must pair start/stop to avoid orphan helpers. Because the implementation may touch system-wide memory controls, lifecycle mistakes have broader impact than ordinary per-process stressors.

## Test Signals
Build coverage validates universal API availability. Runtime signals come from stressors using `--thrash`, especially the kernel coverage script's memory and `brk`/`mmap` cases.
