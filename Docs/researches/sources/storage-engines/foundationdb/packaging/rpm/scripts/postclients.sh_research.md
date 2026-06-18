<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/postclients.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/scripts/postclients.sh

## Purpose
Standalone client postinstall script fragment for RPM packaging.

## Important APIs, Types, And Functions
Deletes stale `/usr/lib64/python2.6/fdb` from old packages and exits 0.

## Control Flow
Runs after client package installation.

## State And Persistence Behavior
Removes old Python binding directory if present.

## Dependencies And Integration Points
Depends on RPM scriptlet execution and legacy Python path assumptions. Mirrors the `%post clients` fragment in the spec.

## Risks And Edge Cases
Broad `rm -rf` is scoped to a specific legacy directory but still destructive. No check is made for symlinks.

## Test Signals
Validated by upgrade tests from affected old packages.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/postclients.sh -->
