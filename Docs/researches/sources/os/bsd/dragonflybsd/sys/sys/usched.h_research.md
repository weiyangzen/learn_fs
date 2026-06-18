# File Research: sources/os/bsd/dragonflybsd/sys/sys/usched.h

## Summary
Userland scheduler control constants and kernel scheduler interface structures.

## Main Responsibilities
- Defines `struct usched`, a scheduler operations table for process acquisition/release, runqueue placement, clock accounting, priority recalculation, fork/exit heuristics, load updates, CPU mask changes, yielding, and CPU migration.
- Defines per-LWP scheduler data union for BSD4 and DragonFly scheduler state.
- Defines scheduler control flags and `usched_set()` operation numbers.
- Declares kernel scheduler instances and scheduler initialization/control functions.

## Important Behavior
The union reserves padding for future expansion and provides scheduler-specific fields while keeping storage embedded in LWP state.

## Risks
Scheduler implementations rely on exact semantics of callbacks and embedded fields. Adding fields or reinterpreting union members can break existing scheduler code and userland `usched_set()` callers.
