# sources/storage-engines/wiredtiger/tools/io-trace-explorer/scripts/trace-wtperf.sh

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/scripts/trace-wtperf.sh -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/scripts/trace-wtperf.sh

### Purpose
`trace-wtperf.sh` runs a WiredTiger `wtperf` workload while capturing block-device traces and WiredTiger verbose read/write logs. It can optionally format a target block device, run `blktrace`, parse with `blkparse`, and generate an `iowatcher` SVG summary.

### Important APIs, Types, and Functions
The script parses `-D DEVICE`, `-d DIR`, `-F FS`, `-O DIR`, `-T TAG`, and `-h`. It resolves `WT_DIR` through `git rev-parse`, expects `build/bench/wtperf/wtperf`, and checks required tools with `exists`. Safety checks validate workload file resolution, mountpoints, block device identity, output tag collisions, and that output directory is on a different device from the workload.

### Control Flow
After argument parsing and dependency checks, predefined workload names are expanded to `bench/wtperf/runners/*.wtperf`. Formatting mode requires explicit directory or device, unmounts/wipes/mkfs/mounts/chowns, and uses a `wt` subdirectory under the mount. Non-format mode removes and recreates the workload directory. The script starts `blktrace` in the output directory, runs `wtperf` with `WIREDTIGER_CONFIG=verbose=[read:2,write:2]`, sleeps, interrupts `blktrace`, then runs `blkparse -t` and `iowatcher`.

### State and Persistence
It mutates the workload directory, may format and mount a block device, writes stdout capture, raw blktrace files, parsed device trace, and summary SVG into the output directory. It also writes WT verbose output to the captured stdout file for later parsing by `io_trace.cpp`.

### Dependencies and Integration Points
Requires Linux tracing tools (`blktrace`, `blkparse`, `iowatcher`), `findmnt`, `stat`, `realpath`, `sudo`, optional `mkfs.*`/`wipefs`, and a compiled WiredTiger `wtperf`. Output feeds `IOTraceExplorer`.

### Risks and Test Signals
Formatting mode is intentionally destructive and relies on explicit device/directory checks; shell quoting is incomplete in several test expressions and commands. `sudo killall -INT blktrace` can affect unrelated blktrace processes. Removing `$WORKLOAD_DIR` in non-format mode is dangerous if misconfigured. Tests should mock `findmnt`, `stat`, and tool availability; integration tests should use disposable loop devices and verify output tag collision protection and device separation checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/scripts/trace-wtperf.sh -->
