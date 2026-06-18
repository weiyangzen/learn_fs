<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-deb -->
# Research: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-deb

## Purpose
Debian postinstall hook for multiversion server packages.

## Important APIs, Types, And Functions
Ensures the `foundationdb` system group/user, creates data/log directories with owner and mode, installs server alternatives for `fdbserver`, `fdbmonitor`, and init script, and initializes `/etc/foundationdb` on first install.

## Control Flow
After alternatives registration, `mkdir /etc/foundationdb` acts as the first-install gate. On first install it generates a random localhost cluster file, copies default config, fixes permissions, starts the init service, and configures a new single-memory database.

## State And Persistence Behavior
Persists system user/group, `/var/lib/foundationdb/data`, `/var/log/foundationdb`, `/etc/foundationdb/fdb.cluster`, `/etc/foundationdb/foundationdb.conf`, alternatives entries, and a running service.

## Dependencies And Integration Points
Depends on Debian `addgroup`, `adduser`, `update-alternatives`, init.d service, `fdbcli`, and versioned package layout. Integrates multiversion server binaries with a single active system service.

## Risks And Edge Cases
Using `mkdir /etc/foundationdb` as a first-install sentinel skips config initialization if the directory already exists but files are missing. Service start/configure failures are not guarded with recovery.

## Test Signals
Acceptance signal is package install on Debian with service start and `fdbcli status` after configure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/multiversion/server/postinst-deb -->
