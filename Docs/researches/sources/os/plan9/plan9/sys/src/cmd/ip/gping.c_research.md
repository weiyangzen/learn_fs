# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/gping.c

Graphical IPv4 ping monitor. It opens Draw/Event windows, sends ICMP echo requests to up to 32 machines, receives replies in helper processes, tracks outstanding requests, RTT, packet loss, and unreachable markers, then plots per-host graphs.

The UI supports adding/dropping RTT and loss graphs from a mouse menu, resizing, colored scrolling graph panes, hash marks, and click-to-inspect historical points. It schedules pings across machines at a configurable interval and uses logarithmic RTT scaling.
