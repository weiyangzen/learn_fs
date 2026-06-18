# sources/storage-engines/foundationdb/fdbserver/core/MutationTracking.cpp

## Purpose
`MutationTracking.cpp` provides optional debug-only tracing for mutations that touch configured keys or ranges. It is guarded by `MUTATION_TRACKING_ENABLED` and explicitly rejected in clean/release builds. When disabled, the public functions return disabled `TraceEvent` objects with near-zero behavioral effect.

## Important APIs, types, and functions
- `debugKeys` and `debugRanges` are global debug filters containing label/key or label/range pairs.
- `debugMutationEnabled` checks a `MutationRef` against those filters and emits a `MutationTracking` trace event with label, context, version, and mutation.
- `debugKeyRangeEnabled` wraps a `KeyRangeRef` as a `MutationRef::DebugKeyRange`.
- `debugTagsAndMessageEnabled` parses a commit blob made of `TagsAndMessage` records and calls `debugMutation` for actual mutation payloads.
- Public functions `debugMutation`, `debugKeyRange`, and `debugTagsAndMessage` dispatch to enabled implementations only when the compile-time flag is set.

## Control flow
Single-mutation tracking first checks explicit debug keys. Clear ranges and debug key ranges use containment/intersection checks against mutation ranges; point mutations compare or test containment against `param1`. It then checks configured debug ranges and returns the first enabled trace event. Commit-blob tracking walks serialized messages, handles version headers, skips log-adapter messages, parses and discards protocol/span context messages, and deserializes ordinary mutations for debug matching.

## State and persistence behavior
There is no database persistence. The only state is process-local debug filter vectors. The code reads serialized commit blob bytes using `BinaryReader` with the current network protocol version and may update the reader protocol version when decoding `LogProtocolMessage`.

## Dependencies and integration points
The implementation depends on `FDBTypes`, `SystemData`, `LogProtocolMessage`, `SpanContextMessage`, and `OTELSpanContextMessage`. Its call sites can annotate specific commit, fetch, or storage flows with `DEBUG_MUTATION` style tracing without changing the data path when mutation tracking is disabled.

## Risks and edge cases
The filter lists are compiled globals and default to broad examples, including an "Everything" range. Enabling this in high-volume contexts can generate large traces and expose key/value data in logs. The code uses a raw peek of four bytes for `VERSION_HEADER`, so callers must pass well-formed commit blobs. Adapter messages are intentionally skipped to avoid duplicate traces.

## Test signals
There are no local tests in this file. Useful validation signals are `MutationTracking` trace events with `Label`, `At`, `Version`, `Mutation`, and optional `MessageTags`; absence of events when disabled is expected.
