<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/blob_rewrite_test.go -->
# sources/storage-engines/pebble/blob_rewrite_test.go

## Purpose
Tests Pebble's blob value separation and blob-file rewrite implementation. It exercises both deterministic datadriven scenarios and randomized rewrite chains that preserve random subsets of live blob values.

## Important APIs, Types, and Functions
`TestBlobRewrite` runs `testdata/blob_rewrite` commands for `init`, `add`, `close-output`, and `rewrite-blob`. It uses `blobtest.Values`, `valsep.ValueSeparation`, `sstable.RawWriter`, a logging in-memory VFS, and `objstorageprovider`. `TestBlobRewriteRandomized` constructs one source blob file and many SSTables, repeatedly runs `newBlobFileRewriter`, and verifies rewritten values through `blob.ValueFetcher`. `constantFileMapping` implements `base.BlobFileMapping` for mapping the logical test blob file to a selected physical output file.

## Control Flow
The datadriven test configures either `PreserveAllHotBlobReferences` or `WriteNewBlobFiles`, writes raw table KVs with inline or blob values, closes output and prints blob references/new blob stats, or constructs a `blobFileRewriter` over named SSTables and target blob metadata. The randomized test writes 1000 values to a blob file, creates 1000 SSTables each referencing one value, then performs 10 rewrite iterations. Each iteration picks a source blob file from the rewrite history, chooses a random non-empty subset of referenced values, rewrites into a new physical file, fetches those values with original block/value handles, and appends the new file to the set of rewrite candidates.

## State and Persistence Behavior
All persistence is in-memory object storage and VFS. The tests deliberately model the production invariant that logical `BlobFileID` remains stable while physical disk file numbers change. Randomized rewrites mutate only test metadata describing which original value indices survive each rewrite. Logging captures file-system/object operations for datadriven expected output.

## Dependencies and Integration Points
The tests touch `valsep`, blob file writers/readers, SSTable raw writers, file cache, block cache, manifest table/blob metadata, object storage, and Pebble test key comparer utilities. They are useful integration tests for the contract between SSTable blob-reference liveness blocks and blob file rewriting.

## Risks and Edge Cases
The randomized test uses time-based seeds, so failures require the logged seed to reproduce. It validates preserved values but not explicitly that omitted values are absent, beyond stats and lower value counts. Datadriven coverage is only as broad as `testdata/blob_rewrite`. The helper `constantFileMapping` always maps a blob ID to the requested disk file, which is appropriate for isolated rewrite validation but bypasses version mapping complexity.

## Test Signals
Strong signals include successful fetch of all preserved values through old handles after rewrite, `stats.ValueCount` bounded by the preserved count, liveness-driven rewrite success in datadriven cases, and expected logging of lazy blob creation and metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/blob_rewrite_test.go -->
