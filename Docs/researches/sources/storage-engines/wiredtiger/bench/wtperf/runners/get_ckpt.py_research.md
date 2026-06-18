# sources/storage-engines/wiredtiger/bench/wtperf/runners/get_ckpt.py

## Purpose
`get_ckpt.py` converts checkpoint messages from wtperf output into simple comma-separated time/state data suitable for plotting checkpoint activity.

## Important APIs, Types, and Functions
It has no functions. It reads stdin, tracks cumulative `time`, and prints `time,state` pairs. Lines ending in `secs` advance time; lines starting with `Finished checkpoint` emit start and stop points.

## Control Flow
The script starts with `0,0`. For each input line, if the stripped line ends with `secs`, it adds field 8 (`split(' ')[7]`) to cumulative seconds. If a checkpoint completion line appears, it converts field 4 milliseconds to seconds with rounding, prints `(time-duration,1)`, then `(time,0)`.

## State and Persistence Behavior
Only in-memory cumulative time is maintained. Output is written to stdout; callers redirect it to `.ckpt` files.

## Dependencies and Integration Points
It depends on wtperf textual output format used by `wtperf_ckpt.sh`. It uses only Python standard `sys`.

## Risks and Edge Cases
Parsing is positional and fragile: minor output wording changes break field indexes. Python 3 division returns floats, but `%d` formatting truncates/raises depending value type; in current code `(int + 500) / 1000` is a float under Python 3 and `%d` expects integer-like, so this path may need `//` for strict Python 3 compatibility.

## Test Signals
Feed representative wtperf checkpoint logs and verify generated on/off intervals. Include Python 3 execution in CI because the shebang uses `python`.
