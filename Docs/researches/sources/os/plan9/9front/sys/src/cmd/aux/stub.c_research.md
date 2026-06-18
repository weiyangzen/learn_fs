# File Research: sources/os/plan9/9front/sys/src/cmd/aux/stub.c

`stub` mounts a minimal 9P filesystem that presents exactly one child name at a requested path. The child can be a file or, with `-d`, a directory. It is useful for satisfying path existence expectations without providing content.

It supports attach, walk, open, read, write rejection, and stat. Root reads list the single child; opening anything other than root is denied. The mountpoint is derived by splitting the supplied `path/name`, and the service is mounted `MBEFORE`.

Option `-D` enables lib9p chatty logging.
