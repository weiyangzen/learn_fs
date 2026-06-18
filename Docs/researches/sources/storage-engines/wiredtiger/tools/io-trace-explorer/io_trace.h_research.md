# sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.h

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.h -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.h

### Purpose
`io_trace.h` declares the data model for I/O trace loading and display: trace kinds, individual operations, named trace series, and collections of related traces.

### Important APIs, Types, and Functions
`io_trace_kind` distinguishes raw device, generic file, and WiredTiger log traces. `io_trace_operation` stores timestamp, action, read/write/sync/barrier/discard flags, byte offset, byte length, duration, and issuing process. It defines `wrap_timestamp` plus timestamp-only comparison operators for sorted lookup. `io_trace` owns a name and vector of operations. `io_trace_collection` exposes `load_from_file`, `traces()`, and protected `add_data_point`, with private loaders for blkparse and WT logs.

### Control Flow
The header itself has no runtime flow, but it defines the insertion and query contract used by `io_trace.cpp` and the GUI. Consumers treat `operations()` as immutable sorted data after loading.

### State and Persistence
Trace state is in-memory only. `io_trace_collection` owns raw pointers in `_traces`, which makes destructor cleanup important and copy semantics dangerous because no copy/move operations are disabled.

### Dependencies and Integration Points
It depends on STL `map`, `string`, and `vector`. `main.cpp` owns one collection per application run, `main_window.cpp` iterates the map to build plot widgets, and `plot.cpp` relies on sorted operation vectors for binary searches.

### Risks and Test Signals
The raw pointer map invites accidental shallow copies and double-free if copied. `operations()` exposes references whose lifetime depends on collection lifetime. `process[32]` is small relative to modern command names. Test signals are compile-time checks for model use, parser tests that assert sorted operations, and UI tests that avoid empty-operation traces because plotting assumes `ops[0]` exists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/io_trace.h -->
