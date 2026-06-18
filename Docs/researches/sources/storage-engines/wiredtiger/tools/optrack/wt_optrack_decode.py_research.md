# sources/storage-engines/wiredtiger/tools/optrack/wt_optrack_decode.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/wt_optrack_decode.py -->
## sources/storage-engines/wiredtiger/tools/optrack/wt_optrack_decode.py

### Purpose
`wt_optrack_decode.py` decodes binary WiredTiger operation tracking logs into text rows consumed by the other optack tools.

### Important APIs, Types, and Functions
`buildTranslationMap` reads `optrack-map` lines mapping numeric function IDs to names. `funcIDtoName` resolves IDs. `parseOneRecord` reads a 16-byte record with `struct.unpack('Qhhxxxx')`: timestamp, function id, and operation type. `validateHeader` reads version/thread type/tsc ratio and, for version 3+, epoch seconds. `getStringFromThreadType` maps thread type 0/1 to external/internal. `parseFile` validates the header, calculates nanosecond timestamps from the TSC ratio, writes an output text file, and counts records. `main` parses CLI options and runs files in parallel.

### Control Flow
The script loads the translation map before spawning workers. Each worker opens a binary log, validates its header, creates `<input>-<threadType>.txt`, writes the epoch timestamp line, then streams records until EOF and writes `opType functionName time` rows.

### State and Persistence
Persistent output is one decoded text file per binary input. The process-global `functionMap` is populated before forking. No checkpointing or partial-file cleanup exists.

### Dependencies and Integration Points
Depends on Python `struct`, multiprocessing, and the binary layout defined in WiredTiger `src/include/optrack.h`. Output feeds `find-latency-spikes.py` and `optrack_to_t2.py`.

### Risks and Test Signals
The unpack format uses native endian/alignment for record parsing (`Qhhxxxx`) while the header uses standard `=III`; portability depends on writer layout and host endianness. `getStringFromThreadType` returns undefined `unknown` for unexpected thread types. `validateHeader` has inconsistent return tuple lengths on failure branches, which can break unpacking. `currentLogVersion` is declared but not used for validation. Tests should cover v2/v3 headers, unknown function IDs, missing map file, truncated records, bad thread type, and multiple parallel inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/wt_optrack_decode.py -->
