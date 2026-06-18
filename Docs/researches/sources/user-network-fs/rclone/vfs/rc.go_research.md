<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/rc.go -->
# sources/user-network-fs/rclone/vfs/rc.go

## Purpose
Registers remote-control endpoints for selecting active VFS instances, refreshing/forgetting directory cache entries, controlling poll interval, listing active VFSes, reporting stats, and managing the VFS upload queue.

## Important APIs, Types, and Functions
Key functions are `getVFS`, `rcRefresh`, `rcForget`, `getDuration`, `getInterval`, `getTimeout`, `getStatus`, `rcPollInterval`, `rcList`, `rcStats`, `rcQueue`, and `rcQueueSetExpiry`. Multiple `init` functions register `rc.Call`s for `vfs/refresh`, `vfs/forget`, `vfs/poll-interval`, `vfs/list`, `vfs/stats`, `vfs/queue`, and `vfs/queue-set-expiry`.

## Control Flow
`getVFS` selects a VFS by `fs` parameter or, for compatibility, the only active VFS. Refresh resolves requested directories and calls `readDir` or `readDirTree`. Forget calls `ForgetAll` or `ForgetPath` by file/dir parameters. Poll interval parses duration and timeout, sends the new interval over `vfs.pollChan`, and returns status. Queue expiry parses queue `id`, `expiry`, and optional `relative` and delegates to the cache writeback queue.

## State and Persistence Behavior
The endpoints mutate in-memory directory caches, `vfs.Opt.PollInterval`, and writeback queue expiry. They do not directly persist data except by influencing later cache, polling, or upload behavior. `getVFS` deletes a valid `fs` parameter from input before downstream validation.

## Dependencies and Integration Points
Depends on global active VFS registry from `vfs.go`, `fs/cache` canonicalization, `fs/rc` parameter helpers, `Dir` cache methods, `vfscache.Cache`, and `writeback.Handle`. These endpoints are externally visible through rclone rc.

## Risks and Edge Cases
Ambiguous active VFS selection returns errors when no `fs` is supplied. `rcRefresh` only accepts string-valued `recursive` and `dir*` parameters. `rcPollInterval` returns an error if the remote lacks change notification. `rcQueue` returns nil output if no cache exists, while `rcQueueSetExpiry` returns an invalid-parameter error without cache. Timeout behavior may leave `PollInterval` unchanged if the poll goroutine does not receive in time.

## Test Signals
`rc_test.go` validates active VFS selection errors, basic refresh/forget output, list output, stats output, and limited poll-interval behavior. Queue and queue expiry are mainly tested through vfscache/writeback tests outside this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/rc.go -->
