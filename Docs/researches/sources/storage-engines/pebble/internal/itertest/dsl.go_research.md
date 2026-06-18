# sources/storage-engines/pebble/internal/itertest/dsl.go

## Purpose
`itertest/dsl.go` defines the DSL used to configure iterator probes that can inject errors, replace returned keys, log operations, or conditionally apply behavior.

## Important APIs, Types, And Functions
`Predicate` aliases `dsl.Predicate[*ProbeContext]`. `NewParser` creates a probe parser and nested predicate parser with operation constants plus `UserKey`. Probe constants/functions include `ErrInjected`, `noop`, `Nil`, `If`, `ReturnKV`, and `Log`. `ErrorProbe`, `ifProbe`, `loggingProbe`, `UserKey`, `returnKV`, and `returnNil` implement the probe/predicate behaviors.

## Control Flow
DSL parsing composes probe wrappers. `If` evaluates its predicate against `ProbeContext` and runs either branch. `ErrorProbe` sets `Return.Err` and clears `Return.KV`. `ReturnKV` replaces the returned KV. `Log` writes operation name, seek key, result, and error into the probe state log.

## State And Persistence Behavior
Probe state is primarily in parser-created values and the shared `ProbeContext`. `OnIndex` predicates from the generic DSL can be stateful. Logs are written to caller-supplied writers; no files are written here.

## Dependencies And Integration Points
It depends on `base`, generic `dsl`, `errorfs.ErrInjected`, Go `token`, and string formatting. It integrates with `probe.go` wrappers and datadriven probe tests.

## Risks And Edge Cases
`ReturnKV` stores a pointer to a parsed KV, so repeated uses return the same object. `Log` panics if value materialization fails. Stack/predicate composition inherits generic DSL panic-on-parse-error behavior.

## Test Signals
`probe_test.go` and `testdata/probes` validate parsing, conditional behavior, error injection, nil returns, return replacement, and logging.
