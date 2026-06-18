# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/local_file_test.go

## Purpose

Defines the streaming-writes suite variant for files created locally through the mounted filesystem. It verifies streaming writes for files with no preexisting GCS object.

## Important APIs, control flow, and dependencies

`streamingWritesLocalFileTestSuite` embeds the common streaming suite. `SetupTest` and `SetupSubTest` call `createLocalFile`, which generates a unique name, builds the mounted path, and opens an O_DIRECT file through `operations.OpenFileWithODirect`. `TestStreamingWritesLocalFileTestSuite` attaches the testify suite and runs all shared streaming-write test methods.

## State, persistence, dependencies, and integration points

The initial state is local-only until streaming upload behavior creates or finalizes an object. Inherited tests check that pre-flush reads come from local streaming buffers, close uploads data to GCS, out-of-order writes synchronize correctly, and deletes prevent unwanted object persistence.

## Risks and test signals

The important risk is confusing local-only file state with already-synced object state, especially on zonal buckets where empty appendable objects may appear earlier. Signals are inherited content checks and object-not-found expectations before close or after deletion.
