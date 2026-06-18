# File Research: sources/os/plan9/9front/sys/src/cmd/faces/dblook.c

## Purpose
Small command-line helper to query the faces database for a user and domain.

## Key Elements
Requires exactly `name domain`, calls `findfile(&f, domain, name)`, and prints the selected face file path.

## Dependencies
Links against the faces database code and includes Plan 9 draw/plumb/regexp/bio headers because `faces.h` and shared objects require them.

## Behavior/Risks
No nil check after `findfile`; a missing face path prints through `%s` with a null pointer depending on Plan 9 formatting behavior. Provides a dummy `killall` to satisfy shared code paths that may report bad regexps.
