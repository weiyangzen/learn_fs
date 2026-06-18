<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.h -->
# sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.h

## Purpose
Declares `BlobGarbageMeter`, a small compaction helper that tracks per-blob-file inflow and outflow of blob references to compute newly generated garbage.

## Important APIs, Types, and Functions
`BlobStats` counts records and bytes. `BlobInOutFlow` stores inflow/outflow stats, validates that outflow does not exceed inflow, and exposes `HasGarbage`, `GetGarbageCount`, and `GetGarbageBytes`. The public methods `ProcessInFlow`, `ProcessOutFlow`, and `flows` are the caller-facing API. Private helpers parse blob index references, process wide-column entities, and add flow entries.

## Control Flow
Callers feed compaction input references to `ProcessInFlow` and output references to `ProcessOutFlow`. After processing, each `BlobInOutFlow` where inflow exceeds outflow represents blob-file garbage introduced by the compaction.

## State and Persistence Behavior
The class owns only an in-memory `std::unordered_map<uint64_t, BlobInOutFlow>`. It performs no persistence and makes no manifest edits itself; callers translate resulting counters into blob garbage metadata.

## Dependencies and Integration Points
The header depends on blob constants, RocksDB status, parsed internal keys, slices, and `BlobIndex`. It is intended for compaction code that sees internal keys and encoded values.

## Risks and Edge Cases
Debug assertions enforce monotonic consistency but release builds still rely on caller ordering and valid compaction streams. The API distinguishes additional garbage from all garbage; newly written output-only blob files are intentionally not tracked unless they also appear in inflow.

## Test Signals
The companion test file checks counter math, valid/invalid input parsing, ignored plain values, TTL rejection, and wide-column entity support.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter.h -->
