<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.cc

## Purpose
Implements compaction-time measurement of additional blob-file garbage. It parses blob references from compaction input and output key/value pairs, aggregates per-file inflow/outflow, and lets callers derive how many blob records/bytes became unreachable.

## Important APIs, Types, and Functions
`ProcessInFlow` and `ProcessOutFlow` delegate to `ProcessFlow`. `ParseBlobIndexReference` parses ordinary `kTypeBlobIndex` values. `ProcessEntityBlobReferences` scans `kTypeWideColumnEntity` values for embedded blob indexes through `WideColumnSerialization::ForEachBlobFileNumber`. `GetBlobReferenceDetails` rejects TTL/inlined indexes and computes physical blob record bytes as value size plus record-header/key adjustment. `AddFlow` updates inflow for input references and outflow only for blob files already seen in inflow.

## Control Flow
For every compaction input/output entry, the meter parses the internal key. Plain values return without state changes. Blob index entries decode a `BlobIndex`; wide-column entities iterate each encoded blob reference. Valid references are added to a per-file `BlobInOutFlow`. Output-only references for new blob files are ignored because they do not represent newly generated garbage in preexisting files.

## State and Persistence Behavior
All state is in-memory in `flows_`, a map from blob file number to counters. No persistent metadata is written. The byte accounting intentionally measures full blob-log record contribution, not just stored value length, by including `BlobLogRecord::CalculateAdjustmentForRecordHeader`.

## Dependencies and Integration Points
The implementation depends on `BlobIndex`, blob log format, RocksDB internal key parsing, value types, and wide-column serialization. It feeds compaction/version-edit logic that updates blob garbage metadata after compaction rewrites or drops references.

## Risks and Edge Cases
Malformed internal keys or blob indexes return errors and should fail the compaction accounting path. TTL and inlined blob indexes are treated as corruption in this non-TTL blob-file meter. Outflow without prior inflow is ignored by design, so caller ordering must process all relevant input references as inflow before output-only new files are considered. Wide-column entities can contain multiple blob references per user key and must all be counted.

## Test Signals
`blob_garbage_meter_test.cc` verifies ordinary blob index inflow/outflow deltas, plain values ignored, corrupt keys/indexes rejected, inlined TTL indexes rejected, and wide-column entity references counted independently.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.cc -->
