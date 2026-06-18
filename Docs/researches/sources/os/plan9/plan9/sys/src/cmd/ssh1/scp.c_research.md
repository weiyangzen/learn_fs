# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/scp.c

Plan 9 SCP implementation using classic scp source/sink protocol over `/bin/ssh`.

Key responsibilities:
- Copies local-to-local, local-to-remote, remote-to-local, and remote-to-remote paths.
- Implements remote source mode (`-f`) and sink mode (`-t`).
- Preserves mode and times with `-p`.
- Recursively copies directories with `-r`.
- Spawns `/bin/ssh` to run remote `scp`.

Important functions:
- `destislocal`, `destisremote`: choose transfer direction.
- `send`, `senddir`: emit SCP protocol records and file data.
- `receive`, `receivedir`: parse SCP protocol records and create files/directories.
- `getresponse`, `sendokresponse`: protocol acknowledgments.
- `remotessh`: fork/exec ssh and connect stdio via pipe.
- `fileaftercolon`: detects `host:path`.

Risks/quirks:
- Uses shell command strings for local `cp` and remote-to-remote cases.
- Fixed buffers for paths and protocol headers.
- Sends filler bytes if local read fails after committing file size.
