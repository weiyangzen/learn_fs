# File Research: sources/os/plan9/9front/sys/src/cmd/rio/fsys.c

9P filesystem server for `rio`. Posts `/srv/rio.<user>.<pid>`, serves `/dev` files, and supports per-window directories under `wsys`.

Implements manual dispatch for version, attach, walk, open, read, write, clunk, stat, and flush. Directory reads synthesize stat records for global files and window ids. Non-directory reads/writes are delegated to xfid worker handlers.

Special behavior: skips serving `snarf`, `screen`, or `kbd` if already supplied externally; mounts `/mnt/wsys` and binds it before `/dev` for child window namespaces.
