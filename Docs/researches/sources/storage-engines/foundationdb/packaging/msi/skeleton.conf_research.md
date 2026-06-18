<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/skeleton.conf -->
# Research: sources/storage-engines/foundationdb/packaging/msi/skeleton.conf

## Purpose
Windows MSI seed `foundationdb.conf` used when no existing CommonAppData config file exists.

## Important APIs, Types, And Functions
Defines monitor restart delay, server public/listen address, `parentpid`, a default `fdbserver.4500` section, backup-agent defaults, and one backup-agent process section.

## Control Flow
The MSI first installs this file, then WiX `IniFile` entries patch cluster-file, command, data, log, parentpid, and backup-agent command paths to the chosen install locations.

## State And Persistence Behavior
Becomes persistent CommonAppData configuration and is marked permanent by the installer flow; data/log paths are also created there.

## Dependencies And Integration Points
Depends on WiX template logic and `fdbmonitor` on Windows. Integrated with `FDBInstaller.wxs.cmake` as the initial config payload.

## Risks And Edge Cases
The skeleton is incomplete by design until MSI patching runs. Manual use without installer substitutions would leave missing command and cluster-file settings.

## Test Signals
Validated indirectly by MSI install and service start tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/skeleton.conf -->
