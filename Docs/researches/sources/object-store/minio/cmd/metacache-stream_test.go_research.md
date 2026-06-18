# sources/object-store/minio/cmd/metacache-stream_test.go

Purpose: This test suite locks down metacache stream reader/writer behavior against a fixed sample stream containing sorted Go source-style object and directory names.

Important APIs and types: Helpers `loadMetacacheSample` and `loadMetacacheSampleEntries` open `testdata/metacache.s2` and create `metacacheReader` instances. Tests exercise `readNames`, `readN`, `readFn`, `readAll`, `forwardTo`, `next`, `peek`, `newMetacacheWriter.write`, and `skip`.

Control flow: The tests compare reader output to `loadMetacacheSampleNames`. They cover full reads, zero-count reads, limited reads, directory inclusion/exclusion, prefix reads for existing and non-existing ranges, callback traversal, channel traversal with a wait group, forwarding to exact and partial names, sequential `next`, repeated `peek` followed by `next`, writer round-trip into a `bytes.Buffer`, and skipping across stream positions.

State and persistence behavior: Persistent input is the fixture file `testdata/metacache.s2`; output is in-memory only. The suite validates reader state transitions, especially that `peek` preserves the current entry for `next`, `readN(0)` is non-consuming, and `skip` advances through the encoded name/metadata pairs.

Dependencies and integration points: Tests depend on the sample stream remaining sorted and on `metaCacheEntry` directory classification. They indirectly protect disk walking and metacache persistence because those systems consume the same stream format and reader APIs.

Risks: The fixture has mostly names and no emphasis on rich object metadata, delete markers, versioned entries, corrupt streams, or concurrent writer stream errors. Because expected names are hard-coded, legitimate fixture regeneration requires updating the large expected slice.

Test signals: Strong signals are exact ordered name equality, expected `io.EOF` at natural stream end, zero-length reads returning no error, prefix reads returning the expected slices, successful writer/readback round-trip, and `skip` returning `io.EOF` when asked to skip past the end.
