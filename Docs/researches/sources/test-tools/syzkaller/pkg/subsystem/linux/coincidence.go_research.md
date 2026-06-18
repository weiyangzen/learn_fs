# sources/test-tools/syzkaller/pkg/subsystem/linux/coincidence.go

## Purpose

`coincidence.go` defines a small pair-count matrix used to infer relationships between Linux subsystems. For every file that matches one or more subsystems, callers record the matched set; the matrix then tells how often each subsystem appears and how often pairs co-occur.

## Important APIs, Types, and Functions

`CoincidenceMatrix` wraps `map[*subsystem.Subsystem]map[*subsystem.Subsystem]int`. `MakeCoincidenceMatrix` constructs an empty matrix. `Record(items ...*Subsystem)` increments all ordered pairs, including self-pairs. `Count(a)` returns the diagonal count for one subsystem. `Get(a,b)` returns a pair count. `NonEmptyPairs` iterates non-diagonal entries through a callback.

## Control Flow

`Record` performs a nested loop over the input slice and calls `inc` for every `(i,j)` pair, so recording `[A,B]` increments `A,A`, `A,B`, `B,A`, and `B,B`. `Count` delegates to `Get(a,a)`. `NonEmptyPairs` walks the nested maps and skips self-pairs before invoking the callback. Missing outer or inner map entries evaluate to zero under Go map semantics.

## State, Dependencies, Risks, and Test Signals

The matrix is mutable and keyed by subsystem pointer identity. It does not persist and is not concurrency-safe. Its main dependency is `pkg/subsystem`. Integration points are `BuildCoincidenceMatrix`, `dropSmallSubsystems`, `dropDuplicateSubsystems`, and `setParents`. Risks include duplicate items in one `Record` call inflating counts, unordered iteration, and silent zero counts for unknown subsystem pointers. `coincidence_test.go` verifies totals, pair counts, and callback enumeration.
