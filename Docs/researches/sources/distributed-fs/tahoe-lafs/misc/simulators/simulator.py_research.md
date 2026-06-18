# sources/distributed-fs/tahoe-lafs/misc/simulators/simulator.py

## Purpose

This older share-placement simulator models servers filling as files are uploaded, then renders an ASCII graph of when servers become full. It appears to support both simple ring placement and permuted peer placement for comparison.

## Important APIs, Types, and Functions

The file defines server/ring simulation helpers, a `go(permutedpeerlist)` upload loop returning servers and doubled-up share counts, `div_ceil`, and `test(permutedpeerlist, iters)`, which runs multiple simulations, aggregates each server's `full_at_tick`, compresses the timeline to about 70 columns, and prints an ASCII chart. The main block parses `--iters=` and `--permute`.

## Control Flow

Direct execution chooses permuted or simple-ring mode, runs `test`, which repeatedly calls `go`, records how many servers fill at each file count, computes cumulative full-server counts per compressed bucket, averages across iterations, and prints a y-axis of servers full against uploaded file counts.

## State, Dependencies, Integration, Risks, and Tests

State is simulated server capacity and aggregate `filledat` arrays. Dependencies are stdlib random/hash/math behavior from the file's earlier definitions. Integration is design analysis around peer permutation and capacity spread. Risks include Python 2 division, likely long runtimes, no structured output, and potential index errors if no server fills. Tests should use reduced server/file constants, deterministic seeds, and validate `div_ceil` plus aggregation behavior.
