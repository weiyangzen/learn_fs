# sources/storage-engines/pebble/internal/itertest/probe.go

## Purpose
`probe.go` implements the iterator-probe wrapper that lets tests observe and modify every `base.InternalIterator` operation.

## Important APIs, Types, And Functions
`OpKind` enumerates seek, movement, and close operations and implements predicate evaluation. `Op` describes an operation, seek key, and mutable return KV/error. `Probe` is the injection interface. `ProbeContext` combines `Op` and `ProbeState`, which holds a comparer and log writer. `Attach` wraps iterators with one or more probes. `MustParseProbes` parses DSL strings. `probeIterator` implements `base.InternalIterator`.

## Control Flow
Every positioning method builds an `Op`, delegates to the inner iterator if present, and calls `handleOp`, which populates errors from `iter.Error` for nil results and invokes the probe. `Close` handles the direct close error separately because close does not return a KV. Bounds/context/tree-step/string operations delegate.

## State And Persistence Behavior
`probeIterator` stores the wrapped iterator, one probe, and reusable probe context. Probe modifications persist in `probeCtx.Op.Return.Err` until overwritten by later operations, which is also what `Error()` returns.

## Dependencies And Integration Points
It depends on `base`, `dsl`, `treesteps`, `context`, `io`, and formatting. It is used by itertest probe DSL tests and can wrap nil iterators for pure probe behavior.

## Risks And Edge Cases
Because `Error()` returns probe context error, injected errors can outlive a single operation until another operation updates context. Wrapping multiple probes nests iterators; ordering is the order supplied to `Attach`. Nil inner iterators are supported but only probes provide results.

## Test Signals
`probe_test.go` exercises DSL-attached nil iterators through common iterator commands, checking logged/injected behavior.
