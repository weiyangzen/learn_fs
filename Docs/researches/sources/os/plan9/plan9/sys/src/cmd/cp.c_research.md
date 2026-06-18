# File Research: sources/os/plan9/plan9/sys/src/cmd/cp.c

Simple Plan 9 file copy command.

It supports copying one file to another or multiple files into an existing directory. `-g` preserves group, `-u` preserves user and group, and `-x` preserves mode and mtime. Directories are rejected; this is not recursive copy. `samefile` compares qid, device, and type metadata to avoid copying a file onto itself.

Data is copied in 8 KiB chunks. On successful copy and requested metadata preservation, it uses `dirfwstat` on the destination fd.
