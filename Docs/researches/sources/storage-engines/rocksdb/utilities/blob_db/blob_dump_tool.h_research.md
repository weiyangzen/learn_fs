## `sources/storage-engines/rocksdb/utilities/blob_db/blob_dump_tool.h`

Purpose: declares the blob log dump utility interface and display modes. It is a small diagnostic API for inspecting persisted `.blob` files outside the normal DB read path.

Important APIs and types: `BlobDumpTool::DisplayType` supports `kNone`, `kRaw`, `kHex`, and `kDetail`. `Run()` is the public entry point taking a filename, key/blob/uncompressed display choices, and summary flag. Private helpers read exact byte ranges, dump header/footer/records, format slices, and format numeric ranges.

Control flow represented by declarations: `Run()` owns the high-level scan; `DumpBlobLogHeader()` and `DumpBlobLogFooter()` bracket record iteration; `DumpRecord()` consumes one record and updates aggregate counters; `Read()` hides buffer management for random reads.

State and persistence behavior: `reader_`, `buffer_`, and `buffer_size_` are transient. The utility does not write or repair files. It depends on blob log header/footer and record layout for interpretation.

Dependencies and integration: includes blob log format, `RandomAccessFileReader`, `Slice`, and `Status`. It is under `blob_db` namespace and is implemented entirely in `blob_dump_tool.cc`.

Risks: the public API prints to stdout rather than returning structured data, so callers cannot easily consume parsed output. There is no explicit configuration for filesystem, file options, or output stream. Display type choices apply independently to key, blob, and uncompressed blob and need to be kept consistent with implementation behavior.

Test signals: coverage is indirect through format readers; no dedicated tests are present in the listed files.
