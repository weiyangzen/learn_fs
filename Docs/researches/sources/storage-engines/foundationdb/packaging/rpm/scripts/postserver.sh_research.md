<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/postserver.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/scripts/postserver.sh

## Purpose
Standalone server postinstall script fragment for RPM packaging.

## Important APIs, Types, And Functions
On initial install, creates cluster file if absent, fixes ownership/mode, enables and starts systemd service, and configures single-memory mode for new DBs; on upgrade, conditionally restarts service.

## Control Flow
Uses RPM `$1` scriptlet argument to distinguish install from upgrade.

## State And Persistence Behavior
Persists cluster file and service enable/start state; may initialize database.

## Dependencies And Integration Points
Depends on `systemctl`, `fdbcli`, `/etc/foundationdb`, and `foundationdb` user/group. Equivalent to the server `%post` body in spec-style packaging.

## Risks And Edge Cases
Assumes `/etc/foundationdb` exists. `$NEWDB` is unset in non-new cases but shell permits test. Configure output is suppressed, hiding diagnostics.

## Test Signals
Validated by RPM install/upgrade service smoke tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/postserver.sh -->
