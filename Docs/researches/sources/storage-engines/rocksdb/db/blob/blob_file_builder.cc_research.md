# sources/storage-engines/rocksdb/db/blob/blob_file_builder.cc

## Purpose
Implements blob-file creation for flush/compaction paths: decide whether a value becomes a blob, open blob files, optionally compress values, write records, close files with footer/checksum metadata, optionally prepopulate blob cache, and return blob indexes.

## Important APIs and Control Flow
The `VersionSet*` constructor delegates to a file-number generator. `Add` ignores empty or below-`min_blob_size_` values, opens a file if needed, compresses via builtin compressor when configured, writes a blob record, closes the file if size limit is reached, warms blob cache if configured, and encodes a `BlobIndex` with file number, offset, stored size, and compression type. `OpenBlobFileIfNeeded` allocates a file number, builds a `BlobFileName`, notifies callback, creates a writable file with no-reopen/no-readers contract, configures IO priority/hints, wraps it in `WritableFileWriter` and `BlobLogWriter`, and writes a header. `CloseBlobFile` appends footer, calls completion callback, records `BlobFileAddition`, logs, and resets counters. `Abandon` reports completion with error and drops open writer.

## State, Dependencies, and Risks
State includes file generator, options, compression objects, callback, output vectors, writer, and per-file count/byte counters. Persistent outputs are blob files and manifest additions. Dependencies include filesystem, checksum handoff, IO tracing, compression, blob log format/writer, blob cache typed interface, and event callbacks. Risks include always storing compressed output even if larger, callback/reporting failures, partial file cleanup relying on `blob_file_paths_`, cache prepopulation using original uncompressed value while blob index size records stored bytes, and sync-point-tested I/O failure paths. `blob_file_builder_test.cc` covers core behavior.
