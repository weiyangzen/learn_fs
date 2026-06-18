<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap.go -->
# sources/security-integrity/libcap/cap/cap.go

## Purpose
Core Go package implementation for Linux process capabilities. It defines capability sets, runtime ABI discovery, process set/get operations, bounding and ambient vector helpers, and syscall abstraction.

## Important APIs, Types, And Functions
Defines `Value`, `Flag`, `Effective`, `Permitted`, `Inheritable`, `Diff`, `Set`, `header`, `syscaller`, `MaxBits`, `NewSet`, `GetPID`, `GetProc`, `(*Set).SetProc`, `GetBound`, `DropBound`, `GetAmbient`, `SetAmbient`, and `ResetAmbient`.

## Control Flow
Lazy initialization probes `capget` with the newest magic, chooses word count, and discovers runtime maximum capability bits by scanning the bounding set. Getters use read syscalls; writers use the POSIX-semantics syscall path selected by `scwStateSC`. `SetProc`, `DropBound`, ambient changes, and reset operations serialize through launch-aware write-state handling.

## State And Persistence Behavior
`Set` stores compressed bitmaps protected by an RW mutex and optional namespace root UID. Process writes mutate kernel credential state for all OS threads through psx-backed syscalls except during launcher callbacks. Package globals cache ABI magic, word count, and max capability values.

## Dependencies And Integration Points
Uses `syscall`, `unsafe`, `sync`, `sort`, and the package syscall adapters from `syscalls.go`. Other files extend `Set` with flag operations, text, file xattrs, IAB, and launch behavior.

## Risks And Edge Cases
Capability writes are security-sensitive and partial failures can leave bounding/ambient operations only partly applied. Runtime max-bit discovery depends on kernel `prctl` behavior. Thread-state consistency relies on psx/all-thread syscall support and correct launch serialization.

## Test Signals
Signals come from package tests and examples: process set round trips, import/export comparisons, text parsing, IAB operations, and launcher state isolation.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap.go -->
