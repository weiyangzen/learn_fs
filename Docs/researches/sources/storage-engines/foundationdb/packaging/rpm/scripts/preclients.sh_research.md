<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preclients.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/scripts/preclients.sh

## Purpose
Standalone client preinstall script fragment for RPM packaging.

## Important APIs, Types, And Functions
Ensures `foundationdb` group and user exist, with home `/var/lib/foundationdb`, shell `/bin/false`, and exits 0.

## Control Flow
Runs before client package install so shared config directories can be owned by the service user/group.

## State And Persistence Behavior
Persists system group/user if absent.

## Dependencies And Integration Points
Depends on `getent`, `groupadd`, and `useradd`. Mirrors the `%pre clients` scriptlet.

## Risks And Edge Cases
Does not validate existing user attributes if a `foundationdb` account already exists.

## Test Signals
Validated by package install tests on clean and preexisting-account systems.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preclients.sh -->
