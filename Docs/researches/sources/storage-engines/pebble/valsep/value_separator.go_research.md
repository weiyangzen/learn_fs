# Research: sources/storage-engines/pebble/valsep/value_separator.go

## Purpose
`valsep/value_separator.go` implements the stateful `ValueSeparator`, which either preserves existing hot blob references or rewrites eligible values into newly created blob files while writing an output SSTable.

## Important APIs, Types, And Functions
The internal mode enum distinguishes `preserveAllHotBlobReferences` from `rewriteAllHotBlobReferences`. `ValueSeparator` tracks input physical blob files, output reference depth, comparer, blob object factory, short attribute extractor, blob writer options, current/global output config, invalid-value callback, scratch buffer, pending references, and per-tier blob writer state.

Constructors are `NewPreserveAllHotBlobReferences` and `NewWriteNewBlobFiles`. Key methods are `SetNextOutputConfig`, `OutputConfig`, `EstimatedFileSize`, `EstimatedReferenceSize`, `Add`, `separateValue`, `preserveBlobReference`, `getWriter`, `closeWriters`, `maybeCheckInvariants`, and `FinishOutput`.

## Control Flow
`Add` preserves lazy blob handles only in preserve mode. Otherwise it resolves the value and either writes it inline or separates it if the key kind is SET/SETWITHDEL and the value meets size or likely-MVCC-garbage criteria. `separateValue` optionally extracts a short attribute, lazily opens a hot-tier blob writer, appends the value, maps the blob handle's file number to the output table's reference ID, and writes an inline blob handle to the SSTable. `FinishOutput` builds manifest blob references for preserved files, closes new blob writers, computes reference size and depth, resets state, and returns metadata.

## State And Persistence
Pending references determine the reference ID encoded into SSTable inline handles. New blob file writers persist separated values and produce physical blob metadata. Preserved references rely on `inputBlobPhysicalFiles` to populate manifest references. State resets after every output SSTable.

## Dependencies And Integration Points
The implementation integrates internal key/value representations, lazy blob fetchers, `manifest.CurrentBlobFileSet`-style metadata, `blob.FileWriter`, `sstable.RawWriter.AddWithBlobHandle`, object storage, storage tiers, invariants, and short attributes. It is used by compactions and external SST blob writing.

## Risks And Edge Cases
Reference ordering is correctness-critical: the inline `ReferenceID` must match the table's `BlobReferences` index. Missing input physical metadata in preserve mode is an assertion failure. `SetNextOutputConfig` treats zero values as "inherit global", so callers cannot override to zero except where semantics define zero globally. Short-attribute extraction errors intentionally fall back to inline values to avoid flush busy loops. Currently all blob references are hot-tier only.

## Test Signals
Policy tests should check preserve and rewrite modes, lazy writer creation, inline fallback for small or unsupported key kinds, MVCC garbage separation, short-attribute error fallback, estimated file/reference sizes, reference depth truncation, state reset after `FinishOutput`, and invariants around preserved value totals.
