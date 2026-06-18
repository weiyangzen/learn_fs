# sources/storage-engines/tikv/components/backup/src/writer.rs

## Purpose
Builds in-memory SST files for backup output and uploads them to external storage with encryption, SHA-256, CRC64-XOR, counts, byte totals, column-family metadata, and rate limiting. It supports both transactional MVCC entries and RawKV entries.

## APIs, Types, And Functions
`CfNameWrap` works around lifetime issues for async CF labels. Internal `Writer<W>` wraps an engine `SstWriter` and tracks `total_kvs`, `total_bytes`, and checksum. `BackupWriterBuilder` derives backup file names from store/region/start key and constructs `BackupWriter`. `BackupWriter` owns default and write CF writers for txn backups, with `write`, `save`, `need_split_keys`, and `need_flush_keys`. `BackupRawKvWriter` writes one CF of raw key/value pairs using `KeyValueCodec`.

## Control Flow
Txn `write` iterates `TxnEntry`s, rejects prewrites, writes non-empty default values to default CF, always writes commit metadata to write CF, and updates checksum/counts against the CF that owns the logical value. `save` uploads default CF only when non-empty and write CF when either CF has data, preserving write records even when values live in default. RawKV `write` decodes destination keys/values for checksum accounting while writing encoded bytes to SST. Upload wraps the SST reader in encryption, SHA-256 hashing, and rate limiting before calling external storage.

## State And Persistence
Buffered SST contents are in memory until `save`. Persistent artifacts are `.sst` files in external storage named from backup file base plus CF. Metadata is returned as `brpb::File` with name, size, sha256, crc64xor, kv totals, CF, and cipher IV.

## Dependencies And Integration Points
Uses `engine_traits` SST builders, `ExternalStorage`, encryption readers, `Sha256Reader`, TiKV transaction entries, key prefixing via `keys::data_key`, backup metrics, and `KeyValueCodec`. The files it returns are consumed by backup metadata assembly and restore paths.

## Risks And Test Signals
Risks include checksum mismatches, missing write CF files for default-only values, incorrect raw API decoding, memory pressure from in-memory SSTs, and upload-size assumptions when encryption changes byte layout. Tests ingest produced SSTs into RocksDB to verify empty output, write-only entries, and default+write CF contents.
