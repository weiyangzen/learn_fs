
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/solaris/build_pkg.sh -->
# Research: sources/sync-backup/rsync/packaging/solaris/build_pkg.sh

## Purpose
`packaging/solaris/build_pkg.sh` builds a legacy Solaris package for rsync by staging a fake install tree, generating `pkginfo` and `prototype`, running Solaris packaging tools, and removing the staging tree.

## Important APIs, Types, and Functions
This shell script has no functions. Important variables are `PKGNAME=SMBrsync`, `BASEDIR=/usr/local`, `VERSION="2.5.5"`, `ARCH=$(uname -p)`, `NAME=rsync`, `FAKE_ROOT=$PWD/$PKGNAME`, and `OUTPUTFILE=$PKGNAME-$VERSION-sol8-$ARCH-local.pkg`.

## Control Flow
The script creates `$FAKE_ROOT`, copies the rsync binary, man pages, README, COPYING, and `tech_report.pdf` from relative paths three levels up, writes package metadata with here-documents, runs `pkgmk -d . -r . -f ./prototype -o`, translates the package with `pkgtrans -os`, moves the output package to the original directory, and removes the fake root.

## State and Persistence
It creates and deletes a staging directory named after `PKGNAME`, and leaves the `.pkg` file in the starting directory. It assumes relative path layout under `packaging/solaris/5.8/` as described in comments.

## Dependencies and Integration Points
It depends on Solaris tools `pkgmk` and `pkgtrans`, `uname`, shell utilities, and prebuilt rsync/manual/documentation artifacts. It is independent of modern release automation.

## Risks
The script is stale: version is hard-coded to `2.5.5`, vendor URL is old, paths assume a specific copied location, and unquoted variables could break with spaces. `mkdir $FAKE_ROOT` fails if a stale staging directory exists. It removes `$FAKE_ROOT` recursively, so variable correctness matters.

## Test Signals
On a Solaris-compatible environment, verify staging tree contents, `pkginfo` metadata, `prototype` ownership/modes, package filename, and installability. In CI, shellcheck/static review and a fake-tools dry run can catch quoting and path regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/solaris/build_pkg.sh -->
