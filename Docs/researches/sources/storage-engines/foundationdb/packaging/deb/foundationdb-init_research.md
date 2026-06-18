# sources/storage-engines/foundationdb/packaging/deb/foundationdb-init

Purpose: This is a SysV init script for managing `fdbmonitor` as the FoundationDB process monitor on non-systemd or init.d-compatible systems.

Important functions: `do_start` checks whether `fdbmonitor` is already running and starts it daemonized with `--conffile`, `--lockfile`, and `--daemonize`. `do_stop` stops the process with TERM/KILL retry and removes the pidfile. The case statement supports `start`, `stop`, `status`, `restart`, and `force-reload`.

Control flow: The script exits early if `/usr/sbin/fdbmonitor` is not executable, sources `/lib/init/vars.sh`, then dispatches on the command argument and logs daemon messages when verbose mode allows.

State and persistence behavior: It manages runtime process state and `/var/run/fdbmonitor.pid`. It reads `/etc/foundationdb/foundationdb.conf` but does not write it.

Dependencies and integration points: It uses `start-stop-daemon`, LSB init conventions, and package-installed `fdbmonitor`. `postinst`, `prerm`, and `postrm` call into this service path when systemd is not available.

Risks: The script comments out `/lib/lsb/init-functions`, but still calls `log_daemon_msg`, `log_end_msg`, and `status_of_proc`, which may be undefined depending on environment. Tests should run start/stop/status under target distributions and verify pidfile cleanup and restart semantics.
