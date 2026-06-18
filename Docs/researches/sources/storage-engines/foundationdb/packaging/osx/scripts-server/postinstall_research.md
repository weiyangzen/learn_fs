<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-server/postinstall -->
# Research: sources/storage-engines/foundationdb/packaging/osx/scripts-server/postinstall

## Purpose
macOS server package postinstall script that finalizes config, loads the LaunchDaemon, and configures a new local database on first install.

## Important APIs, Types, And Functions
Generates `/usr/local/etc/foundationdb/fdb.cluster` if absent, restores `.old` config or promotes `.new`, loads `com.foundationdb.fdbmonitor.plist`, and runs `fdbcli configure new single memory` for new databases.

## Control Flow
First-install detection is based on absent cluster file. Config selection happens before service load; database configuration runs after launchctl load.

## State And Persistence Behavior
Persists cluster file, config file, loaded LaunchDaemon state, and initialized database state under `/usr/local/foundationdb`.

## Dependencies And Integration Points
Depends on launchctl, `/usr/local/bin/fdbcli`, package-installed plist, and config payload. Complements server `preinstall` and server payload generation.

## Risks And Edge Cases
Uses `$NEWDB` without initialization under `set -u` absent, so empty is okay but shellcheck would flag it. Service readiness before `fdbcli` configure is assumed. Existing broken config/cluster files skip recovery.

## Test Signals
Validated by macOS server install tests checking LaunchDaemon and single-memory configure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-server/postinstall -->
