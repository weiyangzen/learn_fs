# sources/storage-engines/rocksdb/util/crc32c.h

Purpose: public declaration header for RocksDB CRC-32C helpers in `ROCKSDB_NAMESPACE::crc32c`.

Important APIs and types: `IsFastCrc32Supported()` returns a descriptive runtime support string. `Extend(init_crc, data, n)` computes CRC over data appended after an existing CRC. `Crc32cCombine(crc1, crc2, crc2len)` combines two unmasked CRCs without rereading the first string. `Value(data, n)` is the zero-initialized convenience wrapper. `Mask()` and `Unmask()` apply the LevelDB/RocksDB storage masking transform using `kMaskDelta`.

Control flow: this header is mostly inline wrappers. `Value()` calls `Extend(0, ...)`. `Mask()` rotates right 15 bits and adds a fixed delta; `Unmask()` subtracts the delta and rotates back.

State and persistence: no mutable state. The mask transform is persisted anywhere embedded CRCs are stored, so `kMaskDelta` and rotate widths are compatibility-sensitive.

Dependencies and integration: includes standard size/integer headers, `std::string`, and the RocksDB namespace header. It is consumed widely by checksum generation, file readers/writers, block formats, tests, and utility code.

Risks: callers must pass unmasked CRCs to `Crc32cCombine()`. Mixing masked and unmasked values silently produces wrong results. The API accepts raw `char*` and length with no ownership or null protection except implementation-specific behavior.

Test signals: direct coverage appears in `crc32c_test.cc` for values, incremental extension, masking, and combine behavior.
