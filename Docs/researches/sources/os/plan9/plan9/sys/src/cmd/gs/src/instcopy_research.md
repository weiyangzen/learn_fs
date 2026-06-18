# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/instcopy

Portable shell helper implementing a limited `install`-style copy command.

Key behavior:
- Accepts `instcopy -c [-m mode] srcfile (dstdir|dstfile)`.
- Parses only `-c` and optional `-m`.
- Validates there are two operands and that the source is a regular file.
- If destination is a directory, appends the source basename.
- Copies to a temporary file named `#inst.$$#` in the destination directory, optionally applies mode, removes the old destination, and renames the temporary file into place.

Research notes:
- This is build/install plumbing, not interpreter logic.
- Variables are unquoted, so paths containing spaces or shell metacharacters are not handled safely.
- The temp name is predictable and process-id based, reflecting legacy portability assumptions.
