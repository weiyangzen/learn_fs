# sources/test-tools/syzkaller/pkg/subsystem/list.go

## Purpose

`list.go` provides a process-local registry for named subsystem lists. It decouples a fuzzing target OS from the implementation-specific subsystem list used by syzkaller services.

## Important APIs, Types, and Functions

The package-level `lists` map stores `registeredSubsystem` values containing a `[]*Subsystem` and a `revision`. `HasList` checks registration. `RegisterList` adds a new named list and panics on duplicate names. `GetList` returns the raw registered list and panics if absent. `ListService` constructs a `Service` from a registered list and revision through `MustMakeService`.

## Control Flow

Callers register lists during package initialization or setup. Later consumers check existence, retrieve the list directly, or request a service wrapper for extraction, lookup by name, and child traversal. Missing names and duplicate registration are treated as programmer errors and panic rather than returning errors.

## State, Dependencies, Risks, and Test Signals

State is global to the Go process and is not concurrency-protected. Registered lists are returned by reference, so callers can mutate shared subsystem objects and affect future lookups. There is no external persistence. Dependencies are only `fmt` and the local service/entity types. Integration points include generated Linux lists and any callers that expose subsystem extraction as a service. Risks include duplicate init registration, test pollution between packages, unsynchronized concurrent registration, and mutation of returned lists. Existing service/list tests elsewhere cover registry and service construction behavior.
