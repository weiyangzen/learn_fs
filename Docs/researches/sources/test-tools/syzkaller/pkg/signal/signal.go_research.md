# sources/test-tools/syzkaller/pkg/signal/signal.go

## Purpose

`signal.go` defines syzkaller's feedback signal abstraction: a set of coverage-like elements with priorities used for corpus minimization and manager/fuzzer signal exchange.

## Important APIs, Types, And Control Flow

`Signal` is `map[elemType]prioType` with methods `Len`, `Empty`, `Copy`, `DiffRaw`, `IntersectsWith`, `Intersection`, `Merge`, and `ToRaw`; `FromRaw` builds a signal from raw `uint64` elements at one priority. `Context` pairs a signal with arbitrary caller context, and `Minimize` returns contexts that own the highest priority for at least one signal element. Priority comparisons are central: an existing element covers a new one only if its priority is greater or equal.

## State, Dependencies, Integration, Risks, And Test Signals

State is caller-owned map data; `Merge` mutates the receiver map and allocates on nil. `Copy` uses `maps.Copy`. Integration points include fuzzer corpus minimization, RPC server max-signal propagation, and feedback deduplication. Risks include map iteration nondeterminism in `ToRaw` and `Minimize`, nil-map behavior callers must understand, and priority semantics being easy to invert. `signal_test.go` specifically covers `IntersectsWith`, including lower-priority non-intersection.
