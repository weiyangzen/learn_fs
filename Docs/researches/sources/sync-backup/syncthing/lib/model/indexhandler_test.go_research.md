# sources/sync-backup/syncthing/lib/model/indexhandler_test.go

Purpose: this test file verifies that large numbers of index update messages can be sent through Syncthing protocol connections using `model.NewFileInfoBatch` without message loss or race detector failures.

Important test: `TestIndexhandlerConcurrency` creates two connected protocol endpoints using paired `io.Pipe` readers and writers. It uses generated `mocks.Model` instances as protocol model callbacks, starts both connections, exchanges empty cluster config and initial index messages for folder `foo`, and then sends 500 batches of 1000 files each from one side to the other.

Control flow: the receiving mock installs `IndexUpdateCalls` to verify every received filename matches the expected batch and index position (`f<batch>-<file>`), increments received entry and batch counters, and marks a waitgroup item done. The sender builds a `FileInfoBatch` with a flush function that calls `c1.IndexUpdate`. For each batch, the test appends 1000 `protocol.FileInfo` values with block hashes, adds one waitgroup item, and flushes. It waits for all receiver callbacks before closing connections and checking sent vs received counts.

State and persistence behavior: there is no database persistence. The state under test is protocol connection state, batch buffering, callback invocation counts, waitgroup synchronization, and transport ordering over pipes.

Dependencies and integration points: it depends on `protocol.NewConnection`, generated protocol mocks, generated model mocks, `testutil.NoopCloser`, and the public `model.NewFileInfoBatch` helper. It exercises real protocol serialization/deserialization and callback dispatch rather than only unit-level batch logic.

Risks: this is a high-volume concurrency test and can expose races when run with `go test -race`. Without the waitgroup, connection close can race with the final outgoing message, so the test explicitly waits for the receiving side to observe all expected batches before closing. The test assumes each `IndexUpdate` contains exactly `files` entries and indexes directly into `idxUp.Files[j]`; a short malformed message would panic or fail loudly.

Test signals: the primary signal is equality between `sentEntries` and `recvdEntries`, plus per-file name order validation and race detector cleanliness. It does not validate index handler database sequence logic directly; it validates the lower-level protocol and batch transport path that index sending relies on.
