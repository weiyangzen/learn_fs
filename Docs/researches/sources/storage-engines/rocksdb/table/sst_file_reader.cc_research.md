# sources/storage-engines/rocksdb/table/sst_file_reader.cc

Purpose: implements the public `SstFileReader` utility API for opening an SST file outside a DB, reading keys through DB-style or raw table iterators, point lookup, multi-get, table property access, checksum verification, and entry-count verification.

Important APIs/types/functions: private `Rep` stores `Options`, `EnvOptions`, immutable/mutable options, a persistent `ReadOptions` for raw table iterators, and the opened `TableReader`. `Open` creates `RandomAccessFileReader` and calls the configured table factory. `Get`, `MultiGet`, `NewIterator`, `NewTableIterator`, `ParseTableIteratorKey`, `GetTableProperties`, `VerifyChecksum`, and `VerifyNumEntries` map public APIs to `TableReader` primitives.

Control flow: `Open` reads file size, opens a random-access file, constructs `TableReaderOptions`, sets `largest_seqno` to `kMaxSequenceNumber` for global-seqno compatibility, then opens the table. `Get` wraps the user key in a `LookupKey`, passes a `GetContext` to the table, reports counters, and translates context state to public `Status`. `MultiGet` constructs parallel `KeyContext`/`GetContext` arrays, sorts key contexts by comparator, calls `TableReader::MultiGet`, and post-processes statuses. DB-style iteration wraps a table internal iterator in `ArenaWrappedDBIter`; raw iteration returns `TableIterator`.

State and persistence behavior: the reader owns one opened immutable table. `roptions_for_table_iter` is intentionally stored in `Rep` so raw table iterators are not backed by a caller-owned temporary `ReadOptions`. Values are returned through `PinnableSlice` or copied strings.

Dependencies/integration points: integrates with table factories, `TableReader`, `GetContext`, `MultiGetContext`, `LookupKey`, `ArenaWrappedDBIter`, `TableIterator`, `ParseEntry`, comparators, merge operators, and statistics.

Risks: caller options must match the SST format/comparator. Blob-backed wide-column values cannot be fetched because no `BlobFetcher` is provided, so lookup should return corruption instead of crashing. Raw table iterators expose internal keys and require parsing. `VerifyNumEntries` trusts table properties and only subtracts range deletions.

Test signals: `sst_file_reader_test.cc` covers basic reads, comparators, global sequence numbers, timestamp behavior, raw table iterators, parsing invalid keys, single get vs multiget, checksum, and entry-count corruption.
