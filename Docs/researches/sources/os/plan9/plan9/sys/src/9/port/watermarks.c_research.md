# File Research: sources/os/plan9/plan9/sys/src/9/port/watermarks.c

## Role

Small utility for tracking current and high-water values with a configured maximum.

## Functions

`initmark` clears a `Watermark`, assigns its max, and stores a display name. `notemark` clamps an input value to `[0, max]`, updates `curr`, raises `highwater` when appropriate, and increments `hitmax` when the max is newly hit from below. `seprintmark` formats the measurement.

## Dependencies

Uses `Watermark` from shared kernel headers and Plan 9 `seprint`.

## Risks

No locking is performed; callers must serialize updates if marks are shared across CPUs or interrupt/process contexts.
