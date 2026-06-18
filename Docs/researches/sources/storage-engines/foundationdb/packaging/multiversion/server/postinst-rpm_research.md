<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-rpm -->
# Research: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-rpm

## Purpose
RPM postinstall hook for multiversion server packages.

## Important APIs, Types, And Functions
Creates the service user/group, prepares data/log dirs, ensures `/usr/lib/foundationdb`, registers alternatives for server binaries and systemd unit, and initializes `/etc/foundationdb` on first install.

## Control Flow
First-install flow generates `fdb.cluster`, copies `foundationdb.conf`, fixes ownership/modes, enables and starts `foundationdb` with systemd, and configures single-memory mode with `fdbcli`.

## State And Persistence Behavior
Persists service account, data/log/config directories, alternatives state, systemd service link, cluster file, and running database state.

## Dependencies And Integration Points
Depends on RPM environment tools, `groupadd`, `useradd`, `systemctl`, `update-alternatives`, and versioned install paths. Connects multiversion RPM server payloads to public systemd service management.

## Risks And Edge Cases
Same first-install sentinel risk as Debian: preexisting `/etc/foundationdb` prevents cluster/config creation. There is no explicit daemon-reload call after service alternative changes.

## Test Signals
Validated by RPM install/upgrade smoke tests checking systemd service and `fdbcli` configure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-rpm -->
