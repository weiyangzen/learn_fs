# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_logmgr.h

## Role

Defines JFS journal on-disk formats, in-memory log structures, log buffer structures, log record types, group-commit flags, and public log-manager entry points.

## Key Definitions

- Log geometry: `LOGPSIZE`, `L2LOGPSIZE`, `LOGPAGES`, `LOGSUPER_B`, `LOGSTART_B`.
- Log superblock: `struct logsuper`, with magic/version, size, state, end LSN, UUID, label, and up to `MAX_ACTIVE` active filesystem UUIDs.
- Log page: `struct logpage`, with matching header/trailer page and EOR fields for torn/split write detection.
- Log record descriptor: `struct lrd`, with common fields plus record-specific unions for commit, sync point, mount, redo/no-redo page, inode extent no-redo, map update, file no-redo, and new page.
- Log vector descriptor: `struct lvd`, used by `lmWriteRecord()` to describe line ranges copied into log records.
- In-memory log: `struct jfs_log`, including active superblock list, journal device, current page/EOR, locks, group commit queue, sync list, write queue, and no-integrity flag.
- Log buffer: `struct lbuf`, a private journal I/O page descriptor.
- Log sync prefix: `struct logsyncblk`, shared layout used by tblocks and metapages on `log->synclist`.

## Public Interfaces

Exports log lifecycle and I/O functions:
`lmLogOpen`, `lmLogClose`, `lmLogShutdown`, `lmLogInit`, `lmLogFormat`, `lmGroupCommit`, `lmLog`, `jfsIOWait`, `jfs_flush_journal`, and `jfs_syncpt`.

## Design Notes

The header encodes the contract between transaction logging, metapage writeback, and recovery. The common `logsyncblk` prefix is especially important because both transaction blocks and metapages are linked into the same log sync list.
