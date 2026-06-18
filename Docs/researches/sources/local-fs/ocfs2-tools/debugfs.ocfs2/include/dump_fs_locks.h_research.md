# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_fs_locks.h

## Role

This header declares the filesystem lock-state dumping entry point.

## API

`dump_fs_locks(char *uuid_str, FILE *out, char *path, int dump_lvbs, int only_busy, struct list_head *locklist)` reads OCFS2 lock state from live debugfs or a saved path, optionally dumps LVBs, filters to busy locks, and filters to selected lock names.

## Dependencies

The implementation depends on lock constants and metadata LVB structures from `ocfs2_internals.h`.
