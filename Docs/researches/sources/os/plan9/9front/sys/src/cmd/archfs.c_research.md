# File Research: sources/os/plan9/9front/sys/src/cmd/archfs.c

A 9P filesystem that mounts mkfs-style archive files as a read-only tree.

Important behavior:
- `gethdr` parses archive header lines into file name, mode, uid, gid, mtime, and length.
- `createpath` creates intermediate directories and final files in an in-memory 9P tree.
- Each file’s aux pointer stores its archive offset and length.
- `fsread` seeks into the archive and serves requested bytes.
- `main` builds the tree from the archive, then `postmountsrv`s it, defaulting to `/mnt/arch`.

This is a compact example of Plan 9 lib9p file-server construction over an archive backing file.
