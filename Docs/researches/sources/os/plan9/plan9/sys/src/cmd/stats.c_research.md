# File Research: sources/os/plan9/plan9/sys/src/cmd/stats.c

This file implements the graphical `stats` monitor for local or remote Plan 9 machines.

Key behavior:
- Samples memory, swap, sysstat counters, Ethernet stats, wireless signal, battery, and CPU temperature.
- Displays one or more scrolling graphs per machine using libdraw/event.
- Can mount remote machines through exportfs/9P to read their `/dev` and `/net` status files.
- Supports graph add/drop through the mouse menu and command-line graph selection flags.
- Handles window resizing, labels, log scaling, y-axis labels, and multiple machine columns.

Important details:
- Local/remote data comes from files including `/dev/swap`, `/dev/sysstat`, `/net/ether0/stats`, `/net/ether0/ifstats`, `/mnt/apm/battery`, `/dev/battery`, and `/dev/cputemp`.
- Remote exportfs setup uses `auth_proxy`, `mount`, and optional old-9P conversion through `srvold9p`.
- Remote reads are alarm-bounded and temporarily disabled after repeated failures.
- Counter graphs compute deltas from previous samples; utilization graphs use current values.
- Mouse handling runs in a shared-memory rfork process.

Filesystem relevance:
- Direct: demonstrates Plan 9’s file-oriented instrumentation model and remote filesystem mounting for monitoring.
