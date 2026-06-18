# File Research: sources/os/plan9/9front/sys/src/cmd/auth/box.c

Namespace/device sandbox wrapper for running commands in a skeletal filesystem view.

Key responsibilities:
- Parses bind options for read/replace/create paths, device exposure flags, debug, and shell mode.
- Starts `skelfs` and mounts skeleton file and directory servers at `/mnt/f` and `/mnt/d`.
- Resolves relative paths against the current directory.
- Constructs a new root under `/mnt/d/newroot.<pid>` by binding skeleton directories/files for required path components.
- Binds requested paths into the new root, replaces `/`, restricts devices through `/dev/drivers`, and execs the target command.

Dependencies:
- Uses Plan 9 namespace operations, `skelfs`, `/dev/drivers`, and auth/libc APIs.

Research notes:
- `-s` shell mode binds `/srv`, `/env`, `/rc`, and `/bin` and runs `/bin/rc`.
- Debug mode prints generated bind and device commands.
