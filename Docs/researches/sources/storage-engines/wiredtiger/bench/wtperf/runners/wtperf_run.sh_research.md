# sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_run.sh

## Purpose
`wtperf_run.sh` runs a wtperf benchmark repeatedly on Jenkins, filters out min/max outliers, averages remaining metrics, and writes normalized results to `wtperf.out`.

## Important APIs, Types, and Functions
Shell functions `getval` and `isstable` compute min/max and 3% stability. Arrays track `avg`, `max`, `min`, `sum`, current metrics, operation names, and output labels. The script parses required config path and run count plus optional wtperf args and `NOCREATE`.

## Control Flow
For each run, it optionally recreates `WT_TEST`, runs `./wtperf -O <config> <args>` with tcmalloc preload and library path extension, archives selected artifacts with `rsync`, extracts load time and operation counts from `WT_TEST/test.stat`, updates min/max/sum, and after three runs may stop early if all metrics are stable. It then computes averages, optionally subtracting min/max, and appends labeled results to `wtperf.out`.

## State and Persistence Behavior
It deletes/recreates `WT_TEST`, writes `wtperf.out`, and creates timestamped backup directories named from the workload, run number, and epoch. It relies on `test.stat` output from wtperf.

## Dependencies and Integration Points
It depends on bash arrays, `bc`, `expr`, `grep`, `cut`, `rsync`, tcmalloc at `/usr/local/lib/libtcmalloc.so`, local `./wtperf`, and Jenkins/perf dashboard parsers expecting labels such as `Insert count:`.

## Risks and Edge Cases
`if test "$numruns" -eq "0"; then $numruns=1; fi` is invalid assignment and can try to run a command named by the value. The initial `avg/max/min/sum` arrays are sized inconsistently before assigning `loadindex=6`, leaving an unused gap. `LD_PRELOAD` hard-coding can fail on systems without tcmalloc. Arithmetic mixes integer `expr` and floating `bc`. Argument logging prints parsed `$#` after shifting, not original count.

## Test Signals
Run with a small wtperf config and 1-3 iterations, with and without `NOCREATE`, and verify `wtperf.out` labels plus archived artifacts. Shellcheck would catch several assignment/quoting issues.
