# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/revdump.c

Read status: complete, 40 lines.

This small utility dumps a reverse proto enumeration. Callback `enm` prints new path, mode flags, uid, gid, and old path for each enumerated file.

`main` accepts `-r root` and one proto file, calls `revrdproto`, and exits. The usage string says `protodump`.

Filesystem relevance: inspection/debug tool for proto-file expansion and metadata enumeration.
