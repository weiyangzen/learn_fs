# sources/sync-backup/bup/dev/prep-for-freebsd-build

## Purpose
Installs FreeBSD build/test dependencies for bup CI.

## Important APIs, Types, and Functions
Uses `pkg update` and `pkg install` for gmake, git, bash, rsync, curl, par2cmdline, readline, duplicity, rsnapshot, pandoc, graphviz, Python 3.11 packages, pytest, and xdist.

## Control Flow
Sets `ASSUME_ALWAYS_YES=yes`, updates package metadata, attempts `rdiff-backup` install tolerantly, then installs the main package set.

## State and Persistence Behavior
Mutates FreeBSD package state.

## Dependencies and Integration Points
Used by Cirrus FreeBSD task before `gmake dev-check`.

## Risks and Test Signals
Risks are package availability/version drift and tolerated rdiff-backup absence. Signal is package install completion.
