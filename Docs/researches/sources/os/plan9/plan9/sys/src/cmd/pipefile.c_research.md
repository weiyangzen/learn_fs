# File Research: sources/os/plan9/plan9/sys/src/cmd/pipefile.c

Plan 9 utility that interposes read and write commands on a file through a pipe device bind.

Key responsibilities:
- Parses `pipefile [-d] [-r command] [-w command] file`.
- Opens the target file for independent read/write streams, or duplicates one `ORDWR` fd with `-d`.
- Binds a pipe device under `/n/temp`, then binds one pipe endpoint over the target file path.
- Starts writer and reader shell commands connected to pipe/file fds.

Important behavior:
- Defaults missing read or write command to `/bin/cat`.
- `connect()` forks a detached process, duping provided fds to stdin/stdout and executing `rc -c`.
- Uses `RFNOTEG` to avoid note propagation to the command itself.
- Leaves child command lifetime independent via `RFNOWAIT`.

Dependencies:
- Uses Plan 9 namespace operations `bind`, `unmount`, pipe device `#|`, `rfork`, and `/bin/rc`.

Notable risks:
- Hard-coded mount point `/n/temp` can collide with concurrent uses.
- Command strings are interpreted by `rc`, so arguments are shell syntax rather than direct argv.
