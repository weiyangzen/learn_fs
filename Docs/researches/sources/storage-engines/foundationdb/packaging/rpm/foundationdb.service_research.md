<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.service -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.service

## Purpose
systemd unit for the RPM-installed FoundationDB service.

## Important APIs, Types, And Functions
Declares network-online ordering, forking service type, pidfile, `ExecStart` invoking `fdbmonitor` with config and lockfile, mixed kill mode, and restart-on-failure with 60 second delay.

## Control Flow
systemd starts the monitor, tracks the pidfile, and restarts the service on failures.

## State And Persistence Behavior
Maintains runtime process/pidfile state and controls monitor-managed server processes; persistent config lives in `/etc/foundationdb`.

## Dependencies And Integration Points
Depends on systemd, `/usr/sbin/fdbmonitor`, config file, and writable `/var/run` pidfile path. Installed by RPM and enabled/started by postinstall scripts.

## Risks And Edge Cases
For `Type=forking`, pidfile creation must be reliable. No hardening directives are present. `After=network-online.target` does not guarantee DNS or coordinator reachability.

## Test Signals
Validated by systemctl enable/start/status during package install tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.service -->
