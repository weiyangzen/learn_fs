# sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/scripts/preinstall

## Purpose

This macOS package preinstall hook removes an existing Tahoe application tree and stale system path registration before a new package install.

## Important APIs, Types, and Functions

The script is Bash with three direct filesystem operations: recursively remove `/Applications/tahoe.app`, remove `/etc/paths.d/tahoe`, and remove `/etc/manpaths.d/tahoe.1` if each exists.

## Control Flow

Installer runs this before payload installation. Each path is checked and removed independently.

## State, Dependencies, Integration, Risks, and Tests

Persistent effects are destructive removal of the app bundle and path files. Integration is `pkgbuild --scripts`. Risks include deleting local user modifications under `/Applications/tahoe.app`, no quoting issue for these constant paths but no error handling, and the likely typo/mismatch where postinstall writes `/etc/manpaths.d/tahoe` but preinstall removes `/etc/manpaths.d/tahoe.1`. Tests should simulate upgrade installs and verify old app files and both possible manpath files are handled as expected.
