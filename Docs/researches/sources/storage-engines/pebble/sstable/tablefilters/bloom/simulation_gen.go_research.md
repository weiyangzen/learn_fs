# sources/storage-engines/pebble/sstable/tablefilters/bloom/simulation_gen.go

## Purpose
Ignored standalone generator for Bloom filter `simulation.md`, including best probe counts and full FPR data.

## Important APIs, Types, And Functions
`main` iterates bits/key up to 20 and probe counts up to 16, calls `bloom.SimulateFPR`, selects the lowest-FPR probe count with a 1 percent tolerance for fewer probes, formats markdown through `ascii.Make`, and writes `simulation.md`.

## Control Flow
The generator first fills FPR tables, then chooses the best probe count per bits/key. It writes a compact best table followed by full data for all simulated combinations.

## State And Persistence Behavior
Only persists the generated markdown file. `//go:build ignore` keeps it out of normal builds.

## Dependencies And Integration Points
Depends on `bloom.SimulateFPR`, `internal/ascii`, and `os.WriteFile`. Its output informs `probes` and comments in `bloom.go`.

## Risks And Edge Cases
Simulation runtime scales with bits/key/probe combinations. The 1 percent tolerance chooses smaller probe counts for speed even if not strictly optimal.

## Test Signals
Manual generation output and consistency with the hard-coded probe table are the signals.
