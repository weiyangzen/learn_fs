# File Research: sources/os/plan9/9front/sys/src/cmd/ip/gping.c

Graphical ICMP monitor. It opens ICMP/ICMPv6 echo channels to up to 32 machines, spawns receiver processes, periodically sends echo requests, tracks outstanding sequence numbers, and graphs RTT and packet-loss data in a Plan 9 draw/event window.

The UI supports multiple graph rows, multiple machines, colorized scrolling plots, resize handling, mouse menu to add/drop RTT or loss graphs, and click-to-inspect historical values.

RTT is log-scaled; loss uses a smoothed percentage and marks unreachable events. Processes are tracked so `killall` can terminate children on exit or failure.
