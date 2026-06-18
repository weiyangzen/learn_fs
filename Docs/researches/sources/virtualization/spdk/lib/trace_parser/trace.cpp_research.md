# File Research: sources/virtualization/spdk/lib/trace_parser/trace.cpp

This file implements the C++ backing object for the C trace parser API. It maps a trace file or shm object read-only, reconstructs chronological trace entries, decodes arguments, and tracks object relationships.

`spdk_trace_parser::init()` opens either a regular file or shm object, maps the header to get the full trace-file size, remaps the full file, and populates an ordered `std::map` keyed by timestamp and lcore. It can parse all lcores or one selected lcore. For all-lcore mode, it detects whether any history ring overflowed; if so, it sets `_tsc_offset` to the highest first timestamp among overflowed histories and suppresses older events so output covers a common time window.

`populate_events()` handles circular trace histories. When a ring is full, it finds the earliest and latest timestamp positions; otherwise it walks from entry zero through the filled prefix. Entries with continuation tpoint IDs are skipped, and entries before the trace clear timestamp are ignored.

`next_entry()` returns decoded parser entries in sorted order. It attaches the source trace entry, lcore, thread name, object index/start time for tracepoints tied to object types, and related-object metadata when tracepoint relation descriptors match a previously seen object. New-object tracepoints create stable per-object indexes.

Argument decoding uses `argument_context` to copy argument bytes from the initial trace entry and continuation buffers. `build_arg()` validates continuation buffer markers and timestamps, copies into the fixed parser argument union, and zeroes integer storage before partial-width copies.

The exported C API wraps object construction/destruction and methods: `spdk_trace_parser_init()`, cleanup, file access, TSC offset, next-entry iteration, and per-lcore entry count. Construction failures are caught and converted to `NULL`.

Important invariants are trace-file size validation before full mmap, continuation-buffer integrity, sorted event ordering with duplicate timestamp tie-breaks by lcore, and object correlation state that depends on chronological iteration.
