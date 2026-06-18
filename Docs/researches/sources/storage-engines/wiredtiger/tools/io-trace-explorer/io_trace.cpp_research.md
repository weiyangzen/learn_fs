# sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.cpp

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.cpp -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.cpp

### Purpose
`io_trace.cpp` loads trace files into sorted in-memory trace series. It supports blkparse device-level output and WiredTiger verbose read/write logs, normalizing records into `io_trace_operation` values grouped by device or logical WiredTiger file category.

### Important APIs, Types, and Functions
`io_trace_collection::load_from_file` opens a file and dispatches based on its first character. `load_from_file_blkparse` parses blkparse `C` completion records, recognizes RWBS flags, converts 512-byte block offsets/lengths to bytes, extracts optional duration/process fields, and stores only reads/writes. `load_from_file_wt_logs` parses WT verbose lines with `[WT_VERB_READ][DEBUG_2]` or `[WT_VERB_WRITE][DEBUG_2]`, accepts `read`, `read-mmap`, `write`, and `write-mmap`, converts absolute timestamps to seconds relative to the first WT record, and stores file-path operations. `add_data_point` creates named `io_trace` buckets and keeps each operation vector timestamp-sorted.

### Control Flow
The parser reads files line by line into fixed 256-byte buffers, tokenizes with `strsep`, validates expected fields, constructs `io_trace_operation`, and calls `add_data_point`. `add_data_point` rewrites names for WT logs into combined logs, main files, table files, or other, and rewrites device traces as `Raw Device: ...`. If appended timestamps are monotonic it pushes back; otherwise it inserts by `std::upper_bound`.

### State and Persistence
All parsed data lives in `io_trace_collection::_traces`, a map from display name to heap-owned `io_trace`. The collection destructor deletes traces. There is no persistence beyond memory; the GUI consumes the collection after all input files load.

### Dependencies and Integration Points
The file depends on C stdio/string parsing, `io_trace.h`, and `util.h::ends_with`. It is called from `main.cpp`, and its `operations()` vectors are read by `plot_widget`.

### Risks and Test Signals
The parser uses fixed 256-byte lines, so long WT paths or verbose prefixes can truncate and cause parse failures or bad grouping. `strncpy(item.process, p, sizeof(item.process))` may leave a non-null-terminated process name if exactly full. `load_from_file_wt_logs` assumes offset and length token positions and simple comma/colon stripping, which is brittle for path names or changed log formatting. Unit tests should cover monotonic and out-of-order insertion, blkparse lines with and without duration/process, WT read/write-mmap lines, log-file grouping, malformed line errors, empty files, and unsupported first-line formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.cpp -->
