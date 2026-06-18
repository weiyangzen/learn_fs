# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/install-sh

Portable shell install helper derived from X11R5 `install.sh`.

Key behavior:
- Supports testing via `DOITPROG=echo`.
- Allows tool overrides through environment variables such as `MVPROG`, `CPPROG`, `CHMODPROG`, `CHOWNPROG`, `CHGRPPROG`, `STRIPPROG`, `RMPROG`, and `MKDIRPROG`.
- Parses BSD-like options: `-c` copy instead of move, `-d` create directory, `-m` mode, `-o` owner, `-g` group, `-s` strip, `-t=` transform sed expression, and `-b=` transform basename suffix.
- Validates source and destination arguments, handles directory destinations by appending the source basename, and emulates `dirname` with sed.
- Creates missing destination directories component by component.
- For directory creation, applies optional owner/group/strip/chmod commands.
- For file installation, copies or moves to a temp file in the destination directory, applies ownership/group/strip/mode changes, removes any previous destination, then renames the temp file into place.

Dependencies:
- Requires `/bin/sh`, sed, basename, and basic file utilities.
- Intended for use by configure-generated Makefiles when a system install program is missing or unsuitable.

Research notes:
- Installs one file at a time.
- Uses an old temp-file name pattern `#inst.$$#`; interrupted installs rely on traps for cleanup.
- Does not quote all path uses consistently by modern standards, so paths with spaces or shell metacharacters are unsafe.
