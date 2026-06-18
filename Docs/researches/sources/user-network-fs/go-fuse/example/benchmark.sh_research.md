# sources/user-network-fs/go-fuse/example/benchmark.sh

Purpose: legacy shell workflow for benchmarking `zipfs` stat performance and optional internal latency monitoring.

Important flow: validates a ZIP input, sets `GOMAXPROCS` from `/proc/cpuinfo`, builds `zipfs` and `bulkstat` with `gomake`, mounts zipfs, generates a file list with `find`, reruns zipfs, runs `bulkstat`, attaches `6prof`, reruns `bulkstat`, unmounts, then runs zipfs with `-latencies` and dumps `.debug`.

State/dependencies: writes under `/tmp`, uses `/tmp/zipbench`, `/tmp/zipfiles.txt`, `zipfs.log`, `fusermount`, `6prof`, `gomake`, Linux `/proc`.

Risks: non-POSIX `==` under `/bin/sh`, missing tools, stale mount cleanup, and unquoted paths. It is useful as manual benchmark documentation but not robust CI. Test signal is manual successful execution and profiler output.
