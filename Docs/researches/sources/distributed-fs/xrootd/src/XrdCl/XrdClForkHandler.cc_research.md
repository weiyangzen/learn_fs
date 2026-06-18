# sources/distributed-fs/xrootd/src/XrdCl/XrdClForkHandler.cc

## Purpose
`XrdClForkHandler.cc` implements coordinated pre-fork and post-fork handling for XrdCl client objects. It prevents worker threads, timers, and user-level file/filesystem objects from carrying inconsistent mutex or network state across `fork()`.

## Important APIs, Types, And Functions
`ForkHandler::Prepare` stops the `PostMaster`, locks the `FileTimer`, and locks all registered `FileStateHandler` and `FileSystem` objects. `Parent` unlocks file and filesystem objects, unlocks the timer, restarts the postmaster, and releases the handler mutex. `Child` calls `AfterForkChild` on file handlers, unlocks all objects, unlocks the timer, finalizes/reinitializes/starts the postmaster, and registers the timer task again.

## Control Flow
The expected sequence is `Prepare` before fork, followed by either `Parent` in the original process or `Child` in the forked child. `Prepare` holds `pMutex` across the fork boundary; parent and child release it after reconstructing their side of runtime state.

## State And Persistence Behavior
The handler maintains raw-pointer sets for file and filesystem objects plus pointers to `PostMaster` and `FileTimer`. No persistent storage exists. Child handling resets process-local network/task state through postmaster finalization and initialization.

## Dependencies And Integration Points
It integrates with `DefaultEnv` logging, `PostMaster`, `TaskManager`, `FileTimer`, `FileStateHandler`, and `FileSystem` lock methods.

## Risks And Test Signals
`Prepare` assumes `pFileTimer` is non-null and calls `pFileTimer->Lock()` unconditionally. Tests or initialization checks should ensure registration order always provides a timer before fork handlers can run. Fork tests should verify no locks remain held in parent or child, postmaster workers are restarted appropriately, and file handlers receive `AfterForkChild`.
