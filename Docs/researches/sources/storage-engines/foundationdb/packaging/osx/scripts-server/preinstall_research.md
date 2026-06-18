<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-server/preinstall -->
# Research: sources/storage-engines/foundationdb/packaging/osx/scripts-server/preinstall

## Purpose
macOS server package preinstall script that prepares for replacing the service/config.

## Important APIs, Types, And Functions
Attempts to create data/log directories using `$SERVERDIR`, unloads an existing LaunchDaemon plist, and moves existing config to `.old`.

## Control Flow
Runs before payload install, stopping the old service first and preserving config for postinstall restoration.

## State And Persistence Behavior
Mutates LaunchDaemon runtime state and renames `/usr/local/etc/foundationdb/foundationdb.conf` to `.old`.

## Dependencies And Integration Points
Depends on launchctl and existing macOS installation paths. Pairs with server postinstall which restores `.old` or promotes `.new`.

## Risks And Edge Cases
`$SERVERDIR` is not normally defined in installer script context, so the initial `mkdir` lines look ineffective or dangerous if unset. Config rename is not atomic across failures between preinstall and postinstall.

## Test Signals
Validated by upgrade/reinstall package tests, especially config preservation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-server/preinstall -->
