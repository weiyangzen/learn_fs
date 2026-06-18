<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/buildpkg.sh -->
# Research: sources/storage-engines/foundationdb/packaging/osx/buildpkg.sh

## Purpose
Builds macOS FoundationDB client and server component packages and combines them into a product installer.

## Important APIs, Types, And Functions
Accepts build and source directories, reads `version.txt`, creates temporary roots, installs client binaries/libraries/headers/Python bindings/backup symlinks/uninstaller, builds `FoundationDB-clients.pkg`, installs server binaries/config/plist/data/log dirs, builds `FoundationDB-server.pkg`, edits `Distribution.xml`, then runs `productbuild`.

## Control Flow
The script exits on errors, removes temporary roots after each component build, and removes intermediate pkg files after productbuild.

## State And Persistence Behavior
Writes package artifacts into `<build>/packages`, temporary filesystem roots, symlinks inside payloads, and mutates `packaging/osx/Distribution.xml` in the source tree.

## Dependencies And Integration Points
Depends on macOS `pkgbuild`, `productbuild`, BSD `sed -i`, built FoundationDB binaries, Python binding files, and packaging resources/scripts. Integrates CMake build artifacts with native macOS installer tooling.

## Risks And Edge Cases
In-place editing of `Distribution.xml` is the main repo-state risk. Unquoted install destinations and legacy Python 2.7 payload paths can break on modern macOS assumptions. Temporary root cleanup is manual after package creation.

## Test Signals
Validated by running the script on macOS and installing the generated pkg, including LaunchDaemon startup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/osx/buildpkg.sh -->
