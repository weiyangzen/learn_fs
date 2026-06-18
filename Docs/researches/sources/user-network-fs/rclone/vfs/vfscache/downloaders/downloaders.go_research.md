<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders.go -->
# sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders.go

## Purpose
Implements range downloader orchestration for VFS cache items. It starts and reuses background download streams, writes downloaded bytes into cache without overwriting existing ranges, wakes waiters when requested ranges arrive, and handles downloader idle/error shutdown.

## Important APIs, Types, and Functions
Key APIs are `Item`, `Downloaders`, `New`, `Download`, `EnsureDownloader`, `Close`, and internal `_ensureDownloader`, `_dispatchWaiters`, `kickWaiters`, `_newDownloader`, `_countErrors`. The `downloader` type provides `Write`, `open`, `close`, `stopAndClose`, `download`, `setRange`, and `getRange`.

## Control Flow
`Download` creates a waiter for a range, ensures a downloader exists, and blocks for waiter completion. `EnsureDownloader` starts or extends a downloader without waiting. `_ensureDownloader` expands ranges by read-ahead, clips to missing data, reuses a downloader if the desired start is within its current window, or starts a new downloader. Downloader goroutines open a chunked reader at an offset, stream via accounting into `downloader.Write`, and kick waiters as ranges become present. A background ticker periodically kicks waiters to recover from missed events/errors.

## State and Persistence Behavior
State is in-memory downloader lists, waiters, error counts, and per-downloader offsets/ranges. Persistence occurs only through the supplied `Item.WriteAtNoOverwrite`, which writes cache data/range state. `Close` cancels context, stops downloaders, waits for goroutines, and closes pending waiters with an error.

## Dependencies and Integration Points
Depends on `fs.Object`, `chunkedreader`, `accounting`, `asyncreader`, `ranges`, `fserrors`, VFS read-ahead/chunk/buffer options, and the cache item implementation. Used by vfscache items to populate local cache ranges on demand.

## Risks and Edge Cases
Unknown-sized source objects are rejected. `max downloaders` is a FIXME, so many distant reads could create many streams. Error policy closes waiters immediately for no-space and after more than ten errors. Idle downloaders stop after five seconds, and streams stop after skipping too much already-present data. Correctness depends on `Item.FindMissing`, `HasRange`, and `WriteAtNoOverwrite` being race-safe.

## Test Signals
`downloaders_test.go` validates blocking `Download` and asynchronous `EnsureDownloader` against a large pattern file, checking downloaded ranges become present and contents are correct through the fake item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders.go -->
