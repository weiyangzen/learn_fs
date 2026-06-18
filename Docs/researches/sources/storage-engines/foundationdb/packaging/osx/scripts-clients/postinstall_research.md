<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-clients/postinstall -->
# Research: sources/storage-engines/foundationdb/packaging/osx/scripts-clients/postinstall

## Purpose
macOS clients package postinstall script for Python bindings.

## Important APIs, Types, And Functions
Runs `/usr/bin/python -m compileall /Library/Python/2.7/site-packages/fdb` and exits 0.

## Control Flow
Executed by Installer after client payload installation.

## State And Persistence Behavior
Creates `.pyc` files under the installed Python 2.7 site-packages directory.

## Dependencies And Integration Points
Depends on system Python at `/usr/bin/python` and the installed `fdb` package directory. Complements the macOS client payload from `buildpkg.sh`.

## Risks And Edge Cases
Modern macOS may not provide Python 2.7 at this path. Compile failures would fail the package unless Installer tolerates the script behavior.

## Test Signals
Validated by macOS package install smoke tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/scripts-clients/postinstall -->
