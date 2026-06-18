# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/data.c

Global data and filesystem backend registration for `9660srv`.

Key contents:
- Defines standard error strings: nonexistent file, permission denied, no filesystem specified, and authentication failure.
- Sets default service name `9660` and default backing file pointer.
- Declares external `isosub` and installs it as the only entry in `xsublist`.

Filesystem relevance: direct but small. It wires the ISO backend into the generic 9P server.
