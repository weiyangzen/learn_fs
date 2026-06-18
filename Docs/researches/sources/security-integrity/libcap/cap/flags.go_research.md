<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/flags.go -->
# sources/security-integrity/libcap/cap/flags.go

## Purpose
In-memory manipulation and comparison of capability `Set` flag bits.

## Important APIs, Types, And Functions
Defines `GetFlag`, `SetFlag`, `Clear`, `FillFlag`, `Fill`, `ErrBadValue`, `bitOf`, `allMask`, `ClearFlag`, `Cf`, deprecated `Compare`/`Differs`, and `(Diff).Has`.

## Control Flow
Operations validate set and value ranges, lock sets, then manipulate compressed 32-bit words. `SetFlag` snapshots old values and rolls back if any requested value is invalid. `FillFlag` duplicates the reference set to avoid deadlocks. `Cf` duplicates the alternate set before comparing flag bitmaps.

## State And Persistence Behavior
Mutates only the in-memory `Set`; no kernel state changes until callers apply it with `SetProc` or file setters.

## Dependencies And Integration Points
Used throughout the package by text parsing, IAB fill, convenience mode setters, launch setup, and tests.

## Risks And Edge Cases
`bitOf` permits values up to `words*32`, while runtime named values may be fewer; kernel validation happens later. Concurrency safety depends on respecting `Set` locks and duplicate-before-compare patterns.

## Test Signals
Signals are all-mask unit tests, text parse/string round trips, import/export mutation loops, and diff detection.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/flags.go -->
