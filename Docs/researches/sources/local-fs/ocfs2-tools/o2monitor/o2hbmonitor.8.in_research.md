# File Research: sources/local-fs/ocfs2-tools/o2monitor/o2hbmonitor.8.in

This manpage documents `o2hbmonitor`, a daemon for monitoring O2CB disk heartbeat latency. It describes configfs/debugfs requirements, default daemon behavior, syslog logging, and options for warning threshold percent, interactive mode, verbose output, and version display.

It notes Linux 2.6.37+ dependency and references `o2cb(7)`. The description aligns with the implementation’s polling of heartbeat region debugfs elapsed-time files.
