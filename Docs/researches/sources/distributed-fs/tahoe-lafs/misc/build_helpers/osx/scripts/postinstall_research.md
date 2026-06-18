# sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/scripts/postinstall

## Purpose

This macOS package postinstall hook registers Tahoe's application binary and manpage directories with system path lookup mechanisms.

## Important APIs, Types, and Functions

The script is procedural Bash. It appends `/Applications/tahoe.app/bin/` to `/etc/paths.d/tahoe` and `/Applications/tahoe.app/docs/man/` to `/etc/manpaths.d/tahoe`.

## Control Flow

After package payload installation, Installer runs this script as root. It captures `PWD` but does not use it, then appends the two path records.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is in `/etc/paths.d/tahoe` and `/etc/manpaths.d/tahoe`. Integration is the macOS package built by `pkgbuild --scripts`. Risks include appending duplicate lines on repeated installs, no error handling, and mismatch with preinstall cleanup path `/etc/manpaths.d/tahoe.1`. Tests should install twice and verify idempotence or duplicate behavior, then confirm shells and `manpath` can discover the installed app paths.
