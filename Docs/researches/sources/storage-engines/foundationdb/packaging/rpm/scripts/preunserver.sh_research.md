<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preunserver.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/scripts/preunserver.sh

## Purpose
Standalone server preuninstall script fragment for RPM packaging.

## Important APIs, Types, And Functions
On erase (`$1 -eq 0`), stops and disables the `foundationdb` service using systemd when present or SysV service/chkconfig otherwise.

## Control Flow
Runs before package removal to prevent `fdbmonitor` from continuing after binaries are removed.

## State And Persistence Behavior
Mutates service running/enabled state only.

## Dependencies And Integration Points
Depends on RPM scriptlet argument, `pidof`, `systemctl`, `/sbin/service`, and `chkconfig`. Complements RPM server package removal.

## Risks And Edge Cases
Service manager detection is simplistic and all service errors are suppressed, so removal can proceed with a still-running process.

## Test Signals
Validated by RPM erase tests checking service is stopped/disabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preunserver.sh -->
