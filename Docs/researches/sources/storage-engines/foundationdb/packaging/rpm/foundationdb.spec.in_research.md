<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.spec.in -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.spec.in

## Purpose
RPM spec template defining FoundationDB server and clients subpackages, scriptlets, file ownership, and package metadata.

## Important APIs, Types, And Functions
Contains `%package server`, `%package clients`, `%prep`, `%pre/%post/%preun` scriptlets, `%files` manifests, service/config/data/log ownership, and placeholders `FDBVERSION`/`FDBRELEASE` expanded by `m4`.

## Control Flow
Build prep extracts staged files. Server pre creates service user and handles old-version config. Server post creates cluster file on first install, enables/starts systemd service, and configures new single-memory database. Preun stops/disables on erase. Client pre creates user/group and post removes stale Python 2.6 files.

## State And Persistence Behavior
Persistent install state includes service account, config/cluster file, service unit, binaries/libraries/headers, docs, data/log dirs with FoundationDB ownership, and running service/database state.

## Dependencies And Integration Points
Depends on RPM scriptlet semantics, systemd, fdbcli/fdbmonitor, staged `install-files.tar.gz`, and RPM macros. Generated and consumed by `buildrpms.sh` for EL9-style RPM packages.

## Risks And Edge Cases
`AutoReq: 0` suppresses automatic dependency discovery broadly. Scriptlets assume systemd paths and do not handle non-systemd in this inlined version. `$NEWDB` is tested even if unset but shell permits it. First-install recovery is limited.

## Test Signals
Validated by rpmbuild plus install/upgrade/remove tests checking files, service, and database configure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/foundationdb.spec.in -->
