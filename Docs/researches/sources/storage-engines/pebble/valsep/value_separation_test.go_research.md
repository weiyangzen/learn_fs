# Research: sources/storage-engines/pebble/valsep/value_separation_test.go

## Purpose
`valsep/value_separation_test.go` datadriven-tests value-separation policies independent of full DB compaction. It checks no-op storage, preservation of existing blob references, rewriting into new blob files, estimates, metadata, and invalid short-attribute handling.

## Important APIs, Types, And Functions
`TestValueSeparationPolicy` manages a `ValueSeparation`, raw SSTable writer, blob test values, in-memory object store, and logging buffer. Datadriven commands include `init`, `add`, `estimated-sizes`, and `close-output`. `errShortAttrExtractor` implements `base.ShortAttributeExtractor` and always returns an error for fallback testing.

## Control Flow
`init` selects `NeverSeparateValues`, `NewPreserveAllHotBlobReferences`, or `NewWriteNewBlobFiles`, parsing input physical blob metadata when preserving references. `add` lazily creates a raw writer and feeds parsed internal KVs, either in-place values or blob handles from `blobtest.Values`. `estimated-sizes` prints current file/reference estimates. `close-output` closes the raw writer, calls `FinishOutput`, and prints created blob metadata and blob reference entries.

## State And Persistence
The test uses an in-memory VFS/object store and increments file numbers for tables and blobs. It persists temporary table and blob objects only inside the test. The value-separation object carries pending reference state until `close-output`, then resets for later outputs.

## Dependencies And Integration Points
It integrates `datadriven`, manifest debug parsing, blob test value parsing, object storage, raw SST writers, logging raw writer wrappers, `testkeys.Comparer`, and short attribute extraction. It is the main policy-level validation surface for `ValueSeparator`.

## Risks And Edge Cases
Preserve mode requires input physical blob metadata for every referenced blob ID. Short-attribute extractor errors are intentionally non-fatal and should fall back to inline SSTable values. The test's output format must remain stable while still exposing enough metadata to catch reference-depth and size regressions.

## Test Signals
Signals include lazy blob file creation, blob reference ordering, preserved versus rewritten references, estimated size accounting, new blob physical metadata, MVCC garbage behavior through policy inputs, and invalid-value callback output.
