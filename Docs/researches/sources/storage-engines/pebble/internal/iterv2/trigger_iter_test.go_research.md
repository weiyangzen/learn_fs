# sources/storage-engines/pebble/internal/iterv2/trigger_iter_test.go

## Purpose
`trigger_iter_test.go` datadriven-tests `TriggerIter` boundary emission and trigger callback behavior.

## Important APIs, Types, And Functions
`testTrigger` records `trigger: key(dir)` events and exposes `drain`. `TestTriggerIter` supports `define`, `iter`, and `continue` commands. It builds an `axisds` region tree from `[start, end)=count` lines and drives `TriggerIter` through `RunIterOps`.

## Control Flow
The `define` command initializes a region tree and prints normalized intervals. The `iter` command initializes `TriggerIter` with optional lower/upper bounds and a test trigger, then runs operations and appends drained trigger events. `continue` runs more operations on the existing iterator.

## State And Persistence Behavior
The region tree, iterator, and trigger event buffer live in the test closure. Golden behavior persists in `testdata/trigger_iter`.

## Dependencies And Integration Points
It depends on `axisds`, `regiontree`, `datadriven`, `crstrings`, `testkeys`, and iterv2 scripted utilities.

## Risks And Edge Cases
Parsing is intentionally simple and assumes valid `[start, end)=count` input. Because triggers are one-shot, datadriven command order matters.

## Test Signals
Golden output verifies interval normalization, boundary keys/spans, trigger event direction, bounds, direction switches, and post-trigger exhaustion.
