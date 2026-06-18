# File Research: sources/local-fs/ocfs2-tools/o2monitor/o2hbmonitor.c

`o2hbmonitor.c` is a daemon/interactive monitor for O2CB disk heartbeat. It discovers the active cluster in configfs, reads dead threshold settings, scans `/sys/kernel/debug/o2hb/*/elapsed_time_in_ms`, resolves heartbeat region devices, and logs warnings when elapsed time exceeds a configured percent of the idle/dead threshold.

Polling adapts between config polling, slow polling, and fast polling after warnings. Verbose mode prints every sampled region to stdout; daemon mode logs through syslog. A SysV semaphore keyed by `O2HB_SEM_MAGIC_KEY` prevents multiple active instances.

Dependencies are configfs, debugfs, syslog, dirent, and SysV semaphores. Risks include reliance on `d_type`, fixed path buffers with `sprintf`, singleton lock semantics that leave semaphore objects behind, and no signal-driven graceful shutdown path.
