<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/buildrpms.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/buildrpms.sh

## Purpose
Builds FoundationDB RPMs from an already-built tree by staging install files and running `rpmbuild` with a generated spec.

## Important APIs, Types, And Functions
Accepts `VERSION` and `RELEASE`, creates temp RPM topdir and install root, installs config, init/systemd service, binaries, libraries, C headers, docs, backup-agent symlinks, and `make_public.py`, tars the install root, expands `foundationdb.spec.in` through `m4`, builds with `fakeroot rpmbuild`, and copies RPMs to `packages`.

## Control Flow
The script runs linearly under `set` default behavior, with trap cleanup for temp dirs and a fixed `.el9` release suffix.

## State And Persistence Behavior
Writes staged files in temp dirs and final RPMs into `packages`; no system install state is modified by build.

## Dependencies And Integration Points
Depends on bash, mktemp, install, dos2unix, tar, m4, fakeroot, rpmbuild, and build outputs in `bin/`, `lib/`, `bindings/c`, and docs. Connects source/build artifacts to `foundationdb.spec.in` package metadata and scriptlets.

## Risks And Edge Cases
Lacks explicit argument validation and `set -e`; missing files may lead to partial or late failures. Hard-coded `/usr/lib64` and `.el9` limit portability.

## Test Signals
Validated by RPM build and subsequent install tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/buildrpms.sh -->
