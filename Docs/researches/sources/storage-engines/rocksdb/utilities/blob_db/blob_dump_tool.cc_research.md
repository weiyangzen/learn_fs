## `sources/storage-engines/rocksdb/utilities/blob_db/blob_dump_tool.cc`

Purpose: implements `BlobDumpTool`, a command-style reader for RocksDB blob log files. It prints blob log header/footer metadata, optionally prints records in raw/hex/detail form, can decompress values for display/summary, and produces aggregate record/key/value sizes.

Important APIs and functions: `Run()` opens a file with default filesystem APIs, wraps it in a 2 MiB readahead random access file, reads header and footer, iterates records until the footer offset, and prints summary counters. `Read()` manages a reusable buffer and enforces exact-size reads. `DumpBlobLogHeader()` decodes `BlobLogHeader` and prints version, column family, compression, and expiration range. `DumpBlobLogFooter()` decodes `BlobLogFooter` when present and otherwise treats the file as lacking a footer. `DumpRecord()` decodes record headers, reads key/value payloads, optionally decompresses, prints selected fields, and advances offsets. `DumpSlice()` formats bytes.

Control flow: file scanning starts at offset zero. Header size establishes the first record offset, footer detection establishes the stopping offset, and each record advances by `BlobLogRecord::kHeaderSize + key_size + value_size`. Decompression is conditional on file-level compression and requested uncompressed output or summary. The function stops and returns an error if a record read, decode, unsupported compression, or decompression fails.

State and persistence behavior: this file is read-only. The only mutable state is the tool's `reader_`, buffer allocation, and buffer size. It relies on persisted blob log wire format from `db/blob/blob_log_format.h`.

Dependencies and integration: uses `FileSystem::Default`, `RandomAccessFileReader`, `NewReadaheadRandomAccessFile`, blob log format structs, compression manager, table format constants, and `Slice` string/hex conversion. It is paired with `blob_dump_tool.h`.

Risks: `DumpSlice(kRaw)` prints arbitrary bytes as a string, which can be unsafe for terminals or binary data. The detail formatter is manual and easy to regress. Summary of uncompressed bytes requires successful decompression and may fail on unknown compression. The tool treats malformed footer as absent, which is useful for open/incomplete files but can hide footer corruption during diagnostics.

Test signals: no direct test file in this work item, but blob file format is indirectly exercised by BlobDB tests and `BlobFile::ReadMetadata`.
