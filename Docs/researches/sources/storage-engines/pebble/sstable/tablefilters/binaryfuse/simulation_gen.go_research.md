# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/simulation_gen.go

## Purpose
Standalone ignored build program that generates binary fuse `simulation.md` documentation.

## Important APIs, Types, And Functions
`main` defines fingerprint widths, average key-set sizes, calls `binaryfuse.SimulateFPR`, formats a markdown table with `ascii.Make`, and writes `simulation.md`.

## Control Flow
The program iterates bits/fingerprint and average sizes, collects FPR/stddev/bits-key results, appends table rows, prints the board, and writes it to disk.

## State And Persistence Behavior
The only persistence is the generated `simulation.md` file in the current package directory. It is excluded from normal builds by `//go:build ignore`.

## Dependencies And Integration Points
Depends on `binaryfuse.SimulateFPR`, `crhumanize`, and `internal/ascii`. It is a documentation generator for policy comments and tuning.

## Risks And Edge Cases
The listed `bitVals` omit 10 even though the implementation supports 10-bit fingerprints, which may be intentional documentation scope or a stale generator choice. Long simulation runs can be CPU-heavy.

## Test Signals
Manual `go run simulation_gen.go` output and the generated markdown table are the primary signals.
