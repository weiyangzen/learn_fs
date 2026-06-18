# sources/storage-engines/tikv/tests/integrations/coprocessor/test_checksum.rs

## sources/storage-engines/tikv/tests/integrations/coprocessor/test_checksum.rs

Purpose: verifies coprocessor checksum results for table and index scans.

Important APIs: `ChecksumRequest`, `ChecksumResponse`, `ChecksumAlgorithm::Crc64Xor`, `ChecksumScanOn`, `REQ_TYPE_CHECKSUM`, `SnapshotStore`, `TikvStorage`, `RangesScanner`, and helper `reversed_checksum_crc64_xor`.

Control flow: `new_checksum_request` builds SI checksum requests at `u64::MAX`. The test inserts product rows, loops over primary/table and secondary index columns, selects the matching range and scan mode, computes an expected checksum by scanning backward with `RangesScanner`, then handles the coprocessor request and compares checksum plus total KV count.

State and persistence: data lives in the in-memory/test engine; expected checksum reads a snapshot at max timestamp. No file persistence.

Dependencies and integration points: TiDB checksum protobufs, API V1 keyspace decoding, DAG storage scanner, MVCC snapshot store. Risks include scan direction, key encoding, and checksum algorithm drift. Test signal is exact checksum equality and total KV count equal to fixture row count.
