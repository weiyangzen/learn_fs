# File Research: sources/os/plan9/9front/sys/src/cmd/rdbfs.c

Remote debugging 9P filesystem. Mounts a synthetic `/proc/<procname>` tree backed by serial debugger commands.

Exposes files like `ctl`, `kregs`, `mem`, `text`, and `status`. Reads/writes to `mem` and `kregs` are sent over the serial port as textual `rADDR`/`wADDR VALUE` commands; `text` proxies a local kernel text file.

Includes a 4-byte memory page cache keyed by address/count to reduce serial traffic, plus `ctl` commands for `kill`, `exit`, `refresh`, and `hashstats`.
