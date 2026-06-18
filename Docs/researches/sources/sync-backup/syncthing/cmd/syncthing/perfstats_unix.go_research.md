# sources/sync-backup/syncthing/cmd/syncthing/perfstats_unix.go

## Purpose
This Go file implements periodic performance statistics collection for supported Unix-like platforms. It is compiled for `!solaris && !windows` and writes process CPU, memory, network throughput, and database-size samples to a tab-separated CSV-like file.

## Important APIs, Types, And Functions
`startPerfStats` launches `savePerfStats` in a goroutine using a filename derived from the current PID. `savePerfStats(file string)` creates the output file, writes a header, and samples every 250 milliseconds. `cpusec` converts `syscall.Rusage` user plus system time to seconds. The generic `rate[T number]` computes per-second deltas for floats and integers, where `number` is constrained by `golang.org/x/exp/constraints`.

## Control Flow
The collection goroutine creates `perfstats-<pid>.csv` and panics if creation fails. It initializes previous resource and memory snapshots, writes a header row, then ranges forever over `time.NewTicker(250 * time.Millisecond).C`. On each tick it reads current resource usage, runtime memory stats, protocol traffic counters, computes elapsed time from the previous sample, normalizes Darwin `Maxrss`, and writes one line containing elapsed time since start, CPU rate, heap-ish memory in KiB, RSS KiB, network input/output rates in KB/s, and database directory size in KiB. Previous counters are updated at the end of each iteration.

## State And Persistence Behavior
The file creates a persistent `perfstats-<pid>.csv` in the current working directory and never closes it because the sampling loop is unbounded for process lifetime. It repeatedly reads the Syncthing database directory size through `locations.Get(locations.Database)` and `osutil.DirSize`, which can be relatively expensive depending on database size and filesystem behavior. It reads process-global network counters from `protocol.TotalInOut`.

## Dependencies And Integration Points
`cmd/syncthing/main.go` calls `startPerfStats` when the corresponding runtime/debug option is enabled. The implementation integrates with Go runtime memory statistics, Unix `getrusage`, Syncthing build flags, configured locations, filesystem utilities, and protocol traffic accounting. The unsupported Solaris/Windows file provides a no-op implementation with the same function signature.

## Risks And Edge Cases
`prevTime` starts as the zero time, so the first computed `timeDiff` is enormous and first-row rates are not meaningful; subsequent rows are meaningful after `prevTime` is set. `os.Create` failure panics, which is acceptable for an explicit diagnostic mode but can terminate startup. The ticker is not stopped, and the file descriptor is not closed during normal process lifetime. `DirSize` every 250 ms can add overhead. RSS units differ by platform, so the Darwin adjustment is necessary but still depends on platform conventions.

## Test Signals
There are no direct tests. Build coverage across Unix targets protects build tags and syscall use. Manual diagnostic validation should check that enabling perf stats creates the expected file, writes the header, and updates rows with plausible CPU/network/database values.
