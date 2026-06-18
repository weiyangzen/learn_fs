# sources/storage-engines/badger/discard.go

## Purpose
`discard.go` implements a persistent, mmap-backed accounting table that tracks how many bytes in each value-log file are discardable. Badger uses this data to choose good value-log GC candidates.

## Important APIs, Types, and Functions
- `discardStats`: embeds `sync.Mutex` and `*z.MmapFile`, stores `Options`, and tracks `nextEmptySlot`.
- `discardFname`: constant `DISCARD`.
- `InitDiscardStats`: opens/creates the mmap file under `opt.ValueDir`, initializes sentinel zero entries, finds the first empty slot, sorts entries, and logs state.
- Sort interface: `Len`, `Less`, `Swap` keep active 16-byte entries sorted by file id.
- Raw helpers: `get`, `set`, `zeroOut`, `maxSlot`.
- `Update(fidu, discard)`: query, reset, increment, or create per-file discard counters under lock.
- `Iterate`, `MaxDiscard`: scan active entries and return the file with the largest discard count.

## Control Flow and State
The file format is a flat array of 16-byte slots: 8 bytes file id and 8 bytes discard bytes, big-endian. Slot zero with file id 0 is the termination sentinel. `Update` binary-searches sorted active slots, mutates counters, appends new positive entries when needed, grows the mmap file by truncating to double size when full, zeroes the next sentinel, and resorts.

## Persistence Behavior
State lives in `ValueDir/DISCARD` and is memory mapped through Ristretto `z.MmapFile`. Because updates write directly into mmap memory, the file survives DB reopen; tests verify counters reload. Growth uses `Truncate`, and initialization creates a 1 MiB file that can store 65,536 entries.

## Dependencies and Integration Points
Integrated with the value-log subsystem via `db.vlog.discardStats` and value-log GC candidate selection. Depends on `encoding/binary`, `sort`, `sync`, `filepath`, `os`, `github.com/dgraph-io/ristretto/v2/z`, and Badger `y` helpers.

## Risks and Edge Cases
Entry with file id 0 doubles as sentinel, so using fid 0 as a real value would be ambiguous; Badger value logs start at 1 in normal operation. `Iterate` is not internally locked, so callers need to use it in safe contexts or through locked methods like `MaxDiscard`. Mmap flush semantics are not explicit in this file.

## Test Signals
`discard_test.go` covers initialization, increments, resets, iteration values, `MaxDiscard` default, and reload persistence across DB reopen.
