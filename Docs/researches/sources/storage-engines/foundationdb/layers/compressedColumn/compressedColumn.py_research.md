# sources/storage-engines/foundationdb/layers/compressedColumn/compressedColumn.py

Purpose: This layer stores a logical column in FoundationDB while compacting adjacent rows into packed chunks. It supports point reads, streaming iteration, and a non-fully-transactional packing pass that merges unpacked rows with existing packed segments.

Important APIs and types: `Column` exposes `setRow`, `getRow`, `delete`, `getColumnStream`, and `pack`. Helper classes `_PackedData`, `_MergedData`, and `_ColumnStream` handle packed serialization, merge cursors, and streaming reads. Keys are tuple-encoded as `(columnName, "unpacked", row)` or `(columnName, "packed", startRow, endRow)`.

Control flow: Point reads first check the unpacked key, then locate the packed segment whose range covers the requested row. `pack` repeatedly opens a transaction, reads batches of unpacked rows, loads overlapping packed data, merges sorted packed/unpacked rows, deletes old unpacked and packed entries, and writes new packed chunks sized by `targetChunkSize`/`maxChunkSize`. `_ColumnStream` fetches packed and unpacked ranges incrementally and merges them into ordered result batches.

State and persistence behavior: Persistent state is divided between unpacked row keys and packed value blobs. `_PackedData` serializes a header of key length, value length, and body offset records followed by concatenated values. Packing is incremental and each chunk commit is independent, so a full column pack is not atomic.

Dependencies and integration points: It uses `fdb.api_version(16)`, tuple keys, `fdb.KeySelector`, `fdb.KeyValue`, and Python `struct`. It is a low-level FoundationDB data-model example that relies on lexicographic row-key ordering.

Risks: The code is Python 2-era and uses raw string byte handling. `pack` has a FIXME for `transaction_too_old` where overlapping packed blocks should be unpacked and retried, so long-running packing can leave work incomplete. Tests should cover point reads across packed/unpacked overlap, stream ordering, pack idempotence, chunk size boundaries, delete behavior, and recovery from retryable transaction errors.
