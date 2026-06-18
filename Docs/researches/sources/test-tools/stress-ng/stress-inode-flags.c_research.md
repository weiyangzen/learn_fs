# sources/test-tools/stress-ng/stress-inode-flags.c

## Purpose
`stress-inode-flags.c` stresses filesystem inode flag and file-attribute interfaces by repeatedly toggling `FS_IOC_GETFLAGS`/`FS_IOC_SETFLAGS` and shimmed `file_getattr`/`file_setattr` flags on a temporary directory and file from several threads.

## Important APIs, Types, And Functions
`stress_data_t` shares directory fd, file fd, and filename. `inode_flags[]` and `attr_flags[]` collect available filesystem flags from `<linux/fs.h>`. `stress_inode_flags_ioctl()` reads current flags, sets or clears a requested bit pattern, then clears the bit. `stress_inode_flags_ioctl_sane()` resets flags to zero so cleanup can remove files. `stress_inode_flags_stressor()` iterates generated flag permutations, individual flags, file-attribute get/set operations, invalid filename/size paths, and bogo increments under a lock. `stress_inode_flags_thread()` runs the same worker function in pthreads.

## Control Flow
The stressor creates a counter lock, generates all flag permutations, makes a temp directory/file, opens directory and file descriptors, starts up to four pthread workers, waits at the barrier, and runs the stressor in the main thread until stop. Teardown stops threads, joins them, resets flags to sane values, closes fds, unlinks the temp file, removes the temp directory, frees permutations, and destroys the lock.

## State And Persistence
State includes shared fds, temp path, `keep_running`, generated permutations, and a lock. Temporary filesystem objects are removed. During execution, inode flags on those temp objects are intentionally changed.

## Dependencies And Integration Points
Requires pthreads, `libgen.h`, `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `O_DIRECTORY`, stress-ng flag permutation, temp filesystem helpers, shim file-attribute APIs, and bogo lock helpers.

## Risks
Some flags are privileged, immutable, filesystem-specific, or incompatible; failures are mostly ignored to maximize coverage. Forgetting final sane reset can leave an immutable/append-only temp file that cannot be removed. Thread workers share fds and global flags, so stop coordination and cleanup ordering matter.

## Test Signals
Signals include clean temp removal after runs, no stuck immutable files, successful threaded join, bogo count progress, tolerated unsupported flags, and invalid attribute calls returning harmless errors.
