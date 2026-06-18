# sources/storage-engines/foundationdb/contrib/alloc_instrumentation_traces.py

Purpose: analyzes `MemSample` JSON trace events from allocation instrumentation and prints top memory users by total size and allocation count.

Important APIs/functions: module-level stdin loop and helper `byte_str`.

Control flow: reads JSON lines from stdin, filters `Type == "MemSample"` and non-`na` backtraces, resets aggregate lists when `Time` changes, stores tuples for count and size ordering, then prints top 10 by size and top 5 by count for the last timestamp seen.

State and persistence: in-memory lists for the current timestamp only; stdout report only.

Dependencies and integration: Python json/stdin and `MemSample` trace schema.

Risks and test signals: only the last timestamp is reported; malformed JSON or missing fields abort; `byte_str` can run past suffixes for extreme sizes. Test with multiple timestamps, `Bt=na`, size/count ordering, and empty input.
