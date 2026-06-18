<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateBase.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateBase.hh

## Purpose

`XrdPfcDirStateBase.hh` defines shared data structures used by both live directory-state trees and flattened snapshot/purge representations.

## Important APIs, Types, And Functions

- `DirUsage` stores last open/close times, disk blocks, open file count, file count, and directory count.
- `DirUsage(const DirUsage&, const DirUsage&)` combines two usage records.
- `DirUsage::update_from_stats()` applies `DirStats` deltas to usage totals.
- `DirUsage::update_last_times()` keeps maximum last-open and last-close timestamps.
- `DirStateBase` stores a directory name.
- `DataFsStateBase` stores filesystem-level usage update time and data/meta capacity/usage fields.

## Control Flow

Live tree code updates `DirUsage` from interval `DirStats`; snapshot and purge structs inherit the same base fields so they can represent equivalent usage without depending on live tree pointers.

## State And Persistence

All fields are plain in-memory counters/timestamps. Snapshot code serializes these fields to JSON, but this header does not perform I/O.

## Dependencies And Integration Points

It includes `XrdPfcStats.hh` and standard `ctime`/`string`. It is included by `XrdPfcDirState.hh`, `XrdPfcDirStateSnapshot.hh`, and `XrdPfcDirStatePurgeshot.hh`.

## Risks And Edge Cases

- Usage updates can go negative if stats deltas are unbalanced.
- `m_StBlocks` is in filesystem blocks, while other code often converts by multiplying by 512; unit consistency matters.
- Combining usage records sums file counts but takes maximum timestamps, which is correct for recency but not for historical distributions.

## Test Signals

Tests should cover `update_from_stats()` for create/remove/open/close/block deltas, combined constructor totals, timestamp max behavior, and serialization compatibility through snapshot code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateBase.hh -->
