<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/fsbenchlist.go -->
# sources/storage-engines/pebble/cmd/pebble/fsbenchlist.go

## Purpose
Defines `pebble bench fs list`, which lists available filesystem benchmarks or prints descriptions for specific benchmark names.

## Important APIs, Types, and Functions
`listFsBench` is the Cobra command. `runListFsBench` calls `bench.FsBenchmarks(vfs.Default)` and prints either all names or selected benchmark name/description pairs.

## Control Flow
With no arguments, it iterates the benchmark map and prints names. With arguments, it looks each name up, prints metadata, and returns an error for an unknown name.

## State and Persistence Behavior
No persistent state is read or written. Output goes to standard output through `fmt.Println`.

## Dependencies and Integration Points
Depends on `bench.FsBenchmarks`, `vfs.Default`, Cobra, and CockroachDB errors. It is attached as a child command in `fsbench.go`.

## Risks and Edge Cases
Map iteration order is nondeterministic, so output ordering may vary. Unknown names abort the command on the first missing benchmark.

## Test Signals
No direct tests. CLI smoke tests should verify non-empty listing and unknown-name error behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/fsbenchlist.go -->
