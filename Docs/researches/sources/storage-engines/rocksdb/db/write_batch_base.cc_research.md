# sources/storage-engines/rocksdb/db/write_batch_base.cc

Purpose: This file provides default `SliceParts` implementations for `WriteBatchBase` mutation APIs. It lets derived classes implement Slice-based methods while still supporting gathered/scattered key and value inputs.

Important APIs/types/functions: Implemented methods are `Put`, `Delete`, `SingleDelete`, `DeleteRange`, and `Merge` overloads taking `SliceParts`, both with and without `ColumnFamilyHandle*`.

Control flow: Each method materializes `SliceParts` into contiguous `std::string` buffers through `Slice(parts, &buffer)`, then delegates to the corresponding `Slice` overload. Delete methods only materialize keys; range delete materializes begin and end keys; put/merge materialize both key and value.

State and persistence behavior: This layer has no persistent state. It may allocate temporary strings to join parts, and the resulting `Slice` remains valid only for the duration of the delegated call. The derived class owns all actual write-batch persistence.

Dependencies and integration points: It depends on `rocksdb/write_batch_base.h`, `rocksdb/slice.h`, and `rocksdb/status.h`. It is used by `WriteBatch`, `WriteBatchWithIndex`, and any other `WriteBatchBase` subclass that does not provide a more efficient gathered-write implementation.

Risks: The fallback copies input parts, so high-throughput callers may prefer specialized overrides. It relies on delegated Slice overloads to enforce size limits, timestamp restrictions, column-family validation, memory limits, and content-flag/protection updates.

Test signals: `write_batch_test.cc` covers gathered `Put` through `PutGatherSlices`; other gathered overloads are indirectly covered by subclasses and API consistency.
