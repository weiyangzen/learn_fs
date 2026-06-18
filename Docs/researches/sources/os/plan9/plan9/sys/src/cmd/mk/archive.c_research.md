# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/archive.c

Implements archive member timestamp support for `mk` targets of the form `archive(member)`.

Key functions:
- `atimeof(force, name)` loads/caches member mtimes and returns the requested member time.
- `atouch(name)` opens or creates an archive and updates a member timestamp if known.
- `atimes(ar)` reads Plan 9 archive headers and installs `S_TIME` symbols for members.
- `type(file)` checks whether a file is an archive and warns once for missing archives.
- `split(name, &member)` parses `archive(member)` and validates archive type.

Behavior notes:
- Long member names are truncated to `SARNAME` for lookup.
- Member mtimes are clamped below aggregate archive mtime to avoid confusing dependency ordering.
- Archive creation writes `ARMAG`.
