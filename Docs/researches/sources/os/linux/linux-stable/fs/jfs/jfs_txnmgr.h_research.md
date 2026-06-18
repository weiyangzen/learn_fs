# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_txnmgr.h

## Role

Defines the transaction manager’s public data structures, flags, overlay lock formats, and entry points.

## Key Definitions

- `tid_to_tblock()` and `lid_to_tlock()` index global transaction and lock tables.
- `struct tblock` represents an active transaction and embeds the logsync prefix, lock list, wait queues, log transaction id, group commit state, commit page/eor, and create/delete-specific union state.
- Commit flags include sync/force/flush, map update modes, create/delete/truncate/lazy, and page/inode element markers.
- `struct tlock` binds a transaction to a metapage or inode and contains a 48-byte overlay region.
- Tlock flags describe page/inode locks, line locks, logged state, update-map state, directory state, writepage/freepage state, and free-lock state.
- Tlock types distinguish inode, xtree, dtree, map, EA, ACL, data, and B-tree root updates.
- `struct linelock` and `struct lv` encode changed line ranges for after-image logging.
- `struct xtlock` stores xtree line state plus low/high/truncate watermarks and inline PXD storage.
- `struct maplock` and `struct xdlistlock` encode allocation/free map updates using inline PXDs or XAD/PXD lists.
- `struct commit` packages transaction commit arguments and a reusable log record descriptor.

## Public Interfaces

Declares transaction lifecycle, lock allocation, map update, EA logging, lazy commit, sync daemon, and quiesce/resume functions.

## Design Notes

The 48-byte `tlock.lock` overlay is central to the design. Multiple logical lock formats must maintain compatible alignment and sizing, so changes here have broad effects on logging and map update code.
