# sources/test-tools/stress-ng/stress-touch.c

## Purpose
Implements the `touch` stressor, which creates and removes many temporary regular files from multiple cooperating processes using either `open(O_CREAT)` or `creat()`. It stresses filesystem metadata operations, open flag handling, temp directory cleanup, and shared bogo counter locking.

## Important APIs, Types, And Functions
`touch_opts_t` maps option tokens to open flags such as direct, dsync, excl, noatime, sync, and trunc when available. `touch_method_t` maps `random`, `open`, and `creat` methods. `stress_touch_opts()` parses comma-separated `touch-opts` through a callback. `stress_touch_dir_clean()` removes leftover regular files from the stress temp directory. `stress_touch_loop()` creates a unique filename from the locked bogo counter, performs the selected file creation method, tolerates or reports selected errno values, closes the fd, and unlinks the file. `stress_touch()` creates children and coordinates start/stop.

## Control Flow
The stressor maps synchronization PID state for four child processes, creates a stress-ng lock named `counter`, resolves options, creates the temp directory, and forks four children. Children wait on per-pid sync, mark run state, enable failure injection, and run `stress_touch_loop()`. The parent waits at the global barrier, releases child sync, enters its own touch loop, then clears the continue flag. Cleanup kills/reaps children, scans and unlinks leftover regular files, removes the temp directory, destroys the lock, and unmaps PID sync state.

## State And Persistence Behavior
State includes a process-shared lock, child PIDs, a temporary directory, and transient files named from monotonically increasing bogo counters. Files are unlinked immediately after close and the directory cleaner catches leftovers after child termination. No intended files persist.

## Dependencies And Integration Points
The file uses stress-ng temp-file naming, process sync, locks, kill/wait, options, random selection, and proc-state helpers. It registers as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`, with `touch-method` and `touch-opts` settings.

## Risks And Test Signals
Some open flag combinations are expected to be unsupported on particular filesystems, especially `O_DIRECT`, `O_NOATIME`, and `O_EXCL` with collisions; selected errno values are logged as failures in the current implementation while other errors are silently ignored. The `creat` method ignores `touch-opts`, and instance zero logs that note. Test signals include bogo counter progress, temp directory cleanup, no leaked child processes, option parser rejection of unknown tokens, and behavior across open/creat/random methods.
