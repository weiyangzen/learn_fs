# sources/storage-engines/wiredtiger/tools/run_parallel.sh

Purpose: repeats an arbitrary shell command for a number of iterations, running multiple parallel copies per iteration.

Important APIs and control flow: validates at least command and iteration count, derives CPU count from `/proc/cpuinfo`, defaults parallelism to half the cores, prints the run configuration, appends iteration markers to `outfile.txt`, shows `df -h .`, launches `num_parallel` copies through `eval nohup $command > nohup.out.$t 2>&1 &`, waits for all PIDs, and on first nonzero exit prints the last 100 lines of that worker's output and exits with the worker status.

State and persistence behavior: writes or appends `outfile.txt` and overwrites `nohup.out.<slot>` in the current directory. It does not clean prior outputs.

Dependencies and integration points: uses Bash, Linux `/proc/cpuinfo`, `seq`, `df`, `nohup`, and shell `eval`. It is a generic stress/repro harness for WiredTiger commands or tests.

Risks: `eval` on the command string means shell metacharacters are interpreted, so callers must treat input as trusted. The Linux-only CPU detection can fail elsewhere, producing weak defaults. Parallel slot outputs are overwritten each iteration. A single failure stops all later iterations but only after the current set has been waited in sequence.

Test signals: visible iteration markers, per-slot `nohup.out.*`, and exit status provide validation. Running `./run_parallel.sh 'true' 1 2` should complete with zero status.
