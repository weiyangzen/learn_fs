# sources/storage-engines/wiredtiger/tools/optrack/optrack_to_t2.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/optrack_to_t2.py -->
## sources/storage-engines/wiredtiger/tools/optrack/optrack_to_t2.py

### Purpose
`optrack_to_t2.py` converts operation tracking text logs into CSV time-series data suitable for T2-style visualization. It aggregates per-function execution time percentages over fixed one-second intervals.

### Important APIs, Types, and Functions
It reuses interval pairing helpers similar to `find-latency-spikes.py`: `assignStackDepths`, `getIntervalData`, `createCallstackSeries`, and `checkForTimestampAndGetRowSkip`. `getSessionFromFileName` extracts a session id from `optrack.<PID>.<session-id>-<type>.txt`. `parseIntervals` creates columns named with T2 metadata (`#units=%;section=Session ...;name=...`) and computes each function's percentage of interval time. `processFile` reads a log and writes CSV. `main` parallelizes one process per input file with optional `-j`.

### Control Flow
For each file, the script reads optional epoch timestamp, parses event/function/timestamp rows into intervals, then iterates from first to last interval. For each interval it accounts for functions that start/end inside, start inside and end later, end inside after starting earlier, or span the full interval. The resulting DataFrame is written next to the source with `.csv` extension.

### State and Persistence
Persistent output is one CSV per input plus hidden per-file error logs. Runtime state is per process, with globals for units and interval length. No combined output is produced.

### Dependencies and Integration Points
Depends on pandas, NumPy, multiprocessing, and text logs from the binary optack decoder. CSV output is intended for a separate T2 visualizer.

### Risks and Test Signals
`percentDuration` uses floor division (`//`) on floats, losing fractional percentages and under-reporting short functions. Interval boundary choices use inclusive comparisons and then advance `currentIntBeginUnits = currentIntEndUnits + 1`, which may skip or double-count boundary timestamps depending on input semantics. Log parsing assumes space-delimited function names. Tests should cover spanning intervals, exact-boundary begin/end times, empty logs, malformed stacks, session id parsing, and percentage sums.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/optrack/optrack_to_t2.py -->
