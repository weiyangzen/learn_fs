# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/tas.c

Implements ARM `tas(long *x)`.

Behavior:
- On `ARMv5`, uses `swp`.
- Otherwise uses `ldrex`/`strex` loop to atomically store `1`.
- Returns previous `0` or `1`; reports corrupted lock values and returns locked for anything else.

Role: ARM spin-lock primitive for drawterm.
