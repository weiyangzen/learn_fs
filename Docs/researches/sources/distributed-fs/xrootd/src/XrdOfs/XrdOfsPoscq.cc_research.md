# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPoscq.cc

## Purpose

This file implements the persistent queue used for POSC pending creates. It records files that must be cleaned up or recovered if a create/write operation does not complete successfully, and reconstructs pending entries at startup.

## Important APIs, types, and functions

The constructor stores logger, OSS pointer, queue filename, file descriptor state, and sync cadence. `Add()` appends or reuses a slot for a pending create. `Commit()` marks a record committed by writing the add timestamp and removes it from the in-memory map. `Del()` optionally unlinks the file and clears the record. `Init()` opens/creates the queue and recovers valid pending records. `List()` reads queue records in read-only diagnostic mode. `ReWrite()` compacts/rebuilds the queue into a `.new` file and renames it into place.

## Control flow

`Init()` opens the queue file, truncates a new/small file to the record offset, or scans existing fixed-size records from `ReqOffs`. Records with empty LFNs, missing files, non-regular files, or non-POSC-pending modes are ignored. Valid records are returned as a linked list and then rewritten compactly, updating `pqMap` with offsets.

`Add()` checks existing file state to avoid deleting already created files. For retry/replacement cases it can return an existing verified offset. Otherwise it fills a `Request`, takes a free slot or extends `pocSZ`, writes the record, increments queue count, and updates `pqMap`. `Commit()` validates offset shape, writes current time into `addT`, and erases the map entry. `Del()` validates, optionally unlinks, clears the record's LFN field, recycles the slot, decrements count, and erases the map entry.

## State and persistence behavior

Durable state is a fixed-record queue file starting at offset 64, with each record containing add time, LFN, user, and reserved bytes. In-memory state includes queue size, pending count, map from LFN to offset, free-slot lists, file descriptor, and sync countdown. `reqWrite()` fsyncs after a configurable number of full-record writes.

## Dependencies and integration points

It depends on `XrdOss` for stat/unlink checks, `XrdSysFD_Open`, POSIX `pread/pwrite/ftruncate/fsync/rename`, and SFS mode flags such as `XRDSFS_POSCPEND`. It integrates with `XrdOfsHandle` POSC offsets and startup recovery.

## Risks and test signals

`VerOffset()` validates only offset shape, not that the offset still belongs to the supplied LFN, so callers must pass trusted offsets. `Add()` decrements `pocIQ` under a second explicit lock even though `XrdSysMutexHelper` already holds the mutex; this path warrants scrutiny for deadlock depending on mutex semantics. `ReWrite()` does not fsync the directory after rename. Tests should cover new queue creation, corrupt/short records, retry add behavior, commit/del offset validation, free-slot reuse, rewrite compaction, unlink errors, sync cadence, and recovery of only POSC-pending regular files.
