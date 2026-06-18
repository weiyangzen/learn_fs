# sources/storage-engines/tikv/tests/integrations/coprocessor/test_select.rs

## sources/storage-engines/tikv/tests/integrations/coprocessor/test_select.rs

Purpose: broad integration suite for DAG select coprocessor behavior: table/index scans, streaming, aggregation, ordering, limits, expressions, locks, cache hints, scan details, batch requests, index lookup, commit-ts column output, and API V2 row checksums.

Important APIs and helpers: `DagSelect`, `DagChunkSpliter`, `handle_select`, `handle_request`, `handle_streaming_select`, `ProductTable`, `ColumnBuilder`, `TableBuilder`, `SelectResponse`, `Chunk`, `Expr`, `ExprDefBuilder`, `ScalarFuncSig`, `Context`, `IsolationLevel`, `StoreBatchTask`, `StoreBatchTaskResponse`, `Lock`, TLS engine helpers, and constants `FLAG_IGNORE_TRUNCATE`/`FLAG_TRUNCATE_AS_WARNING`.

Control flow: tests initialize product table rows through helper stores/endpoints, build DAG requests with projections, filters, grouping, aggregate functions, order/limit, index scans, batch tasks, or custom contexts, then decode response chunks and compare encoded datum rows. Early tests validate chunk sizing, streaming ranges, leader-lease reads, failed read futures, scan/time details, table/index group-by and aggregates, delete visibility, filters, truncate errors/warnings, default column values, output offsets, locks, output counts, snapshot errors, coprocessor cache hits, RC reads, bucket version refresh, V2 checksum row formats, multi-region batch task result/error partitioning, nonzero process wall time, local index lookup with intermediate outputs, and `_tidb_commit_ts` placement.

State and persistence: data is committed, deleted, locked, or split across simulated raft regions; some tests mutate lock CF, region buckets, and TLS Rocks engine region info. No durable files are written.

Dependencies and integration points: coprocessor DAG executor, storage MVCC, raftstore region metadata, TiDB expression/protobuf encoding, cache/version semantics, scan statistics, and API V2 row format. Risks include many exact datum expectations, async raft timing, regional split assumptions, cache version assumptions, and lock conflict semantics. Test signals are exact row encodings, error fields, exec details, cache hit flags, lock info, and batch response classifications.
