<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_reader.cc

## Purpose
Implements random-access blob file reads for individual and batched blob references. It validates blob file headers/footers, enforces column-family and TTL expectations, optionally verifies record CRCs, handles compressed values, supports direct I/O and prefetch buffers, and exposes a footer-skipping mode for in-flight direct-write files.

## Important APIs, Types, and Functions
`Create` opens the file, reads the header, optionally validates the footer, initializes decompression state, and constructs a `BlobFileReader`. `OpenFile` creates the `RandomAccessFileReader`, obtains file size using open-handle-first fallback logic, and relaxes direct reads when footer validation is skipped. `GetBlob` validates offset and compression, reads either the value or full record depending on checksum verification, verifies record metadata when requested, decompresses if needed, and returns `BlobContents`. `MultiGetBlob` batches sorted read requests into `FSReadRequest` arrays and processes per-request statuses. Helpers include `ReadHeader`, `ReadFooter`, `ReadFromFile`, `VerifyBlob`, and `UncompressBlobIfNeeded`.

## Control Flow
Reader creation follows open, size check, header decode, optional footer decode, decompressor setup. Single reads compute an adjustment from the value offset back to the record header when checksums are enabled, attempt a prefetch-buffer cache read first, fall back to file read, optionally verify key/value sizes and CRC, then produce uncompressed contents. Multi-read validates each request first, only emits reads for valid requests, performs one `MultiRead`, maps results back to original requests, verifies/decompresses successful records, and accumulates bytes for successful reads.

## State and Persistence Behavior
`BlobFileReader` is read-only and owns a `RandomAccessFileReader`, cached compression metadata, optional decompressor, stats/clock pointers, file size, and `has_footer_`. The footer flag changes offset validation so direct-write files without a footer can be read up to current file size. Read calls update blob bytes-read counters, perf counters, and decompression timing but do not mutate persistent state.

## Dependencies and Integration Points
The implementation depends on blob log format, `BlobContents`, file prefetch buffer, `RandomAccessFileReader`, file naming, file-size helper utilities, compression managers, table multiget constants, sync points for tests, statistics, and RocksDB read options. It is used by `BlobFileCache`, `BlobSource`, version-backed blob reads, and direct-write fallback reads.

## Risks and Edge Cases
Offset validation must account for footer presence, record-header adjustment, user-key length, and overflow-safe end checks. `skip_footer_validation` disables direct reads because direct I/O cannot safely handle the changing tail of an open direct-write file. MultiGet bookkeeping is delicate because validation failures mean the adjustments vector is shorter than the original request array. Corruption during cached-reader reads may be caused by stale footer-less readers, so higher layers refresh readers on corruption. Unsupported compression types produce decompressor failures during creation or decode.

## Test Signals
`blob_file_reader_test.cc` covers normal reads, checksum and no-checksum modes, multiget, stale path-level file sizes, unsupported open-handle size fallback, propagated size errors, malformed/truncated files, TTL rejection, column-family mismatch, CRC and decode corruption injection, Snappy compression and decompression errors, injected I/O errors, and the multiget validation-index regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader.cc -->
