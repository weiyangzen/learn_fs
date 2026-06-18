# File Research: sources/os/plan9/9front/sys/src/cmd/aux/reboot.c

`reboot` is a watchdog utility. It forks into the background, repeatedly `dirfstat`s a target file once every five minutes, and reboots via `/dev/reboot` if the stat fails for a reason other than an alarm timeout.

If no file is supplied, it builds a default path from `/env/cputype` as `/<cputype>/lib`. The watchdog request itself is alarm-limited to 60 seconds. This is intended to detect loss of a critical fileserver connection while tolerating temporary slowness.
