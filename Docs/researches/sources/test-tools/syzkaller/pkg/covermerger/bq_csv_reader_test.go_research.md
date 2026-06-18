# sources/test-tools/syzkaller/pkg/covermerger/bq_csv_reader_test.go

Purpose: tests `gcsGZIPMultiReader` over one or more mocked gzipped GCS files.

Important APIs/types/functions: `TestGCSGZIPMultiReader_Read`, `makeGCSClientMock`, `readCloserMock`, and `gzBytes`.

Control flow: table cases build gzipped byte payloads, configure a mocked GCS client to return per-byte readers, read all bytes from the multi-reader, close it, and compare bytes/errors. Cases cover single file, multiple reads, multiple files, and a corrupt final gzip payload.

State and persistence: no real GCS; in-memory mocks only.

Dependencies and integration: uses syzkaller GCS mock package, testify mock/assert, gzip, and `io.ReadAll`.

Risks: mock file reader returns one byte per read, which exercises streaming but not larger buffer behavior. It does not test `initGCSMultiReader` listing or BigQuery export.

Test signals: good coverage for sequential shard reading and cleanup/error propagation on gzip header failures.
