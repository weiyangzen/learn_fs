# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_note.c

## Purpose

Provides the handler for `/proc/<pid>/note` and `/proc/<pid>/notepg`.

## Main Entry Point

`procfs_doprocnote()` trims and finishes the sbuf, then returns `EOPNOTSUPP`.

## Integration Points

Registered by `procfs.c` as write-only `note` and `notepg` entries with `procfs_attr_w` and `procfs_candebug`.

## Risks and Review Notes

The file is a stub: writes are accepted into the pseudofs buffer but no signal/notification action is implemented. Consumers expecting historical procfs note semantics receive `EOPNOTSUPP`.
