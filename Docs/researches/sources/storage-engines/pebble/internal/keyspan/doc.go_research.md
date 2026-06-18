# sources/storage-engines/pebble/internal/keyspan/doc.go

## Purpose
Documents the `keyspan` package as Pebble's general machinery for sorting, fragmenting, and iterating over ranges of user keys.

## Important APIs, Types, And Functions
The package comment introduces `Span`, `Key`, `Fragmenter`, and non-overlapping fragmented span iterators. It also directs Pebble-specific manifest-aware implementations to the `keyspanimpl` subpackage.

## Control Flow
There is no executable control flow. The file establishes package-level concepts and invariants for generated documentation and readers.

## State And Persistence Behavior
No state or persistence exists in this file.

## Dependencies And Integration Points
It integrates with Go package documentation. The concepts described are implemented by `span.go`, `fragmenter.go`, iterator adapters, and `keyspanimpl`.

## Risks And Edge Cases
Documentation must stay aligned with the fragment/non-overlap contract. If new span kinds or iterator contracts are added without updating this file, higher-level users may miss important invariants.

## Test Signals
No direct tests target this file; compile and documentation generation are the only mechanical signals.
