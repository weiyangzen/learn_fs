<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/iab.go -->
# sources/security-integrity/libcap/cap/iab.go

## Purpose
IAB abstraction for Linux inheritable, ambient, and bounding capability vectors.

## Important APIs, Types, And Functions
Defines `IAB`, `Vector`, `Inh`, `Amb`, `Bound`, `IABDiff`, `NewIAB`, `IABGetProc`, `IABFromText`, `String`, `SetProc`, `GetVector`, `SetVector`, `Fill`, `Cf`, `ProcRoot`, and `IABGetPID`.

## Control Flow
Text parsing interprets prefixes `!`, `^`, and `%` into bound/ambient/inheritable vectors. `SetProc` builds a temporary process capability set, raises `SETPCAP` if needed, resets ambient bits, raises requested ambient bits, and drops bounding bits. `/proc/<pid>/status` parsing derives IAB for other processes.

## State And Persistence Behavior
`IAB` stores three locked bitmap slices. Applying it mutates process inheritable, ambient, and bounding state, with bounding drops irreversible. `ProcRoot` changes a package-global procfs root.

## Dependencies And Integration Points
Uses core `Set` operations, `GetAmbient`, `GetBound`, `DropBound`, `SetAmbient`, `/proc` parsing, and text/name mappings.

## Risks And Edge Cases
Ambient bits require matching inheritable bits; setters enforce this coupling. Bounding vector is represented inverted as `nb`, which is easy to misuse. `/proc` hex parsing depends on field width matching `words`.

## Test Signals
Signals are IAB text round trips, vector coupling checks, fill behavior, PID 1 parsing, and process apply behavior in integration use.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/iab.go -->
