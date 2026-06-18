## sources/test-tools/syzkaller/syz-manager/stats.go

`stats.go` defines manager runtime stats and `initStats`. It creates counters/gauges for crashes, crash types, suppressed reports, fuzzing time, uptime, average VM restart time, Go heap/VM memory, uncompressed image memory/count, and filtered coverage.

Most stats are backed by `stat.Val` and some use functions to read atomics/runtime memory/pool boot time on demand. Prometheus export is configured for total crashes. These stats feed logs, HTTP status, and dashboard upload deltas from `dashboardReporter`.

State is in the stat registry and manager fields. Risks include stats depending on `mgr.pool` for boot time after pool initialization, unit formatting inconsistencies, and global stat registry side effects in tests. There are no direct tests here.
