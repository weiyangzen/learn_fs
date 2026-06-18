# sources/test-tools/syzkaller/pkg/subsystem/service.go

## Purpose

`service.go` wraps subsystem extraction with lookup and hierarchy indexes. It is the package-level service object for consumers that need extraction plus named access, revision tracking, and child lookup.

## Important APIs, Types, And Functions

`Service` embeds `*Extractor` and stores `Revision`, `perName`, and `perParent`. `MakeService` validates non-empty unique subsystem names, builds an extractor, indexes by name, and builds parent-to-children slices. `MustMakeService` panics on construction errors. `ByName`, `List`, and `Children` expose lookup helpers.

## Control Flow, State, Dependencies, And Integration

The service state is computed at construction and then read-only unless callers mutate subsystem objects. `List` iterates a map and therefore returns nondeterministic order. `Children` clones stored slices to protect the internal slice header. The type integrates with registered lists and any syzbot or dashboard code that needs stable named subsystems.

## Risks And Test Signals

Risks include duplicate or missing names failing service construction, pointer identity in `perParent`, and nondeterministic `List` order. `service_test.go` covers child lookup for a single parent but not validation errors or list ordering.
