<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/ycsb.go -->
# sources/storage-engines/pebble/internal/mkbench/ycsb.go

Purpose: implements `mkbench ycsb`, converting raw YCSB benchmark logs into a `data = {...};` JavaScript data file while preserving previously cooked days.

Important APIs/types: `getYCSBCommand`, `ycsbRun`, `ycsbWorkload`, `ycsbLoader`, `newYCSBLoader`, `addRun`, `loadCooked`, `loadRaw`, `cook`, `cookWorkload`, `cookDay`, and `parseYCSB`.

Control flow and state: `loadCooked` parses an existing JS assignment, unwraps JSON, reconstructs workload/day runs, and marks days as cooked. `loadRaw` walks `$date/pebble/ycsb/$name/$run/$file`, skips cooked days, decompresses `.bz2` or `.gz`, scans benchmark lines, parses metrics, and appends runs. `cookDay` averages multiple runs after excluding ops/sec outliers more than one standard deviation from the mean. `cook` writes pretty JSON with the JS prefix/suffix.

Persistence and integration: reads raw logs plus optional existing cooked file and writes a cooked JS file. Integrates with Cobra, compression readers, `walkDir`, and `prettyJSON`. Risks include `log.Fatal` exits on malformed cooked input or write failures, possible divide by zero if all runs are excluded as outliers, day-level cooked skipping across all workloads, scanner limits, and stderr-only raw parse errors. Tests cover from-scratch and incremental fixtures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/ycsb.go -->
