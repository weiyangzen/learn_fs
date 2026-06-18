# sources/storage-engines/wiredtiger/tools/io-trace-explorer/util.h

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/util.h -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/util.h

### Purpose
`util.h` provides small inline helpers shared by the I/O Trace Explorer.

### Important APIs, Types, and Functions
`current_time()` returns wall-clock seconds using `gettimeofday`. `ends_with(std::string_view, std::string_view)` performs suffix checking.

### Control Flow
Both functions are straight-line inline helpers. `current_time` fills a `timeval`, converts seconds plus microseconds to `double`, and returns it. `ends_with` checks size and then compares the suffix.

### State and Persistence
No state is stored or persisted.

### Dependencies and Integration Points
It depends on `<sys/time.h>` and `<string_view>`. `current_time` is used for load/render timing; `ends_with` is used by trace name classification.

### Risks and Test Signals
`gettimeofday` is wall-clock and can move backward; monotonic timing would be better for performance measurements. Suffix tests should cover empty suffix, suffix longer than string, exact match, and mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/util.h -->
