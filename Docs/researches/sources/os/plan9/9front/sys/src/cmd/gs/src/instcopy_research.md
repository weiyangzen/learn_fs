# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/instcopy

Portable shell wrapper for install-like file copying.

Key behavior:
- Accepts `instcopy -c [-m <mode>] <srcfile> (<dstdir>|<dstfile>)`.
- Parses `-c` and optional `-m`.
- Validates that exactly two positional arguments remain and that the source is a regular file.
- If destination is a directory, appends the source basename.
- Copies to a temporary file named `#inst.$$#` in the destination directory, optionally chmods it, removes the old destination, then renames the temporary file into place.
- Installs a trap to remove the temp file on exit.

Notable dependencies:
- POSIX-style `/bin/sh`, `cp`, `chmod`, `rm`, `mv`, `basename`, and `sed`.

Research notes:
- This is build/install tooling, not interpreter runtime code.
- Paths and variable expansions are unquoted, so filenames containing spaces or shell metacharacters are not handled safely.
- The temp filename is predictable and process-ID based, reflecting old portable-install-script conventions.
