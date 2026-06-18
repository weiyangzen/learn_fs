# sources/storage-engines/pebble/internal/blobtest/handles.go

Purpose: Test helper for parsing human-readable blob handles, synthesizing values, fetching lazy blob values, writing blob files, and mapping blob file IDs to inline reference IDs.

APIs and types: `Values`, `FetchHandle`, `ParseInternalValue`, `IsBlobHandle`, `Parse`, `ParseInlineHandle`, `IsEmpty`, `WriteFiles`, `References`, and `MapToReferenceID`.

Control flow and state: `Values.Parse` reads `blob{...}` fields, fills omitted file/block/value IDs from recent handles, defaults length to value length or 12, records explicit or synthesized values, and tracks most recent handles. `FetchHandle` decodes a handle suffix and returns tracked or deterministic derived bytes. `WriteFiles` groups handles by blob file, sorts them, fills value-ID gaps with derived values, writes blobs through `blob.FileWriter`, and returns file stats.

Persistence and dependencies: Writes real blob objects via caller-provided `objstorage.Writable` factory. Depends on base lazy values, blob handle encoding, string parser, slices/cmp, rand/v2, and CockroachDB errors.

Integration points: Used by table/blob tests that need debug text fixtures and lazy value fetching without a full DB.

Risks: Parser recovers panics into errors but still depends on exact debug syntax. Derived values are deterministic but artificial. `WriteFiles` assumes blob file IDs map directly to disk file numbers for tests.

Test signals: No direct test in this subset, but it is support code for blob/value-separation tests.
