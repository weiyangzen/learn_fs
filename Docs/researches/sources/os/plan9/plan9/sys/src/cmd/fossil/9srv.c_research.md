# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9srv.c

Console command support for publishing fossil services through `/srv` or `#s`.

`srvFd` creates an ORCLOSE service file and writes an fd number into it. `srvAlloc` tracks active service registrations, refuses live duplicate names, and cleans stale entries. The `srv` command can list services, delete a service, publish a normal 9P connection, or publish a raw console connection with `-p`.

Flags set connection policy bits such as auth bypass, IP checking, `none` permission, permission bypass, and wstat allowance. Service lifetime is tied to the kept service fd, so registrations disappear automatically on process exit.
