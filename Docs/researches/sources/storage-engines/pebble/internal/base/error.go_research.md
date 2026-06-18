# sources/storage-engines/pebble/internal/base/error.go

Purpose: Defines common Pebble sentinel and categorized errors, including not-found, corruption, assertion failures, panic catching, and corrupt block data attachment.

APIs and types: `ErrNotFound`, `ErrCorruption`, `MarkCorruptionError`, `IsCorruptionError`, `CorruptionErrorf`, `CorruptBlockData`, `AttachCorruptBlockData`, `ExtractCorruptBlockData`, `AssertionFailedf`, and `CatchErrorPanic`.

Control flow and state: Corruption errors are marked through the CockroachDB errors library and recognized by marker lookup. `CorruptBlockData` wraps a cause and stores the corrupted bytes. `CatchErrorPanic` recovers panics that carry errors while re-panicking non-error payloads.

Persistence and dependencies: No persisted state. Depends on `github.com/cockroachdb/errors`, markers, and `invariants` to decide whether assertion failures are marked as safe details.

Integration points: Used throughout Pebble for stable error classification, especially corruption handling and invariant/assertion failures.

Risks: Losing wrappers or markers can break `errors.Is`/classification. `AttachCorruptBlockData` stores byte slices by reference, so callers must avoid unintended mutation if inspecting later.

Test signals: `error_test.go` verifies corrupt block data can be attached and extracted through wrapping.
