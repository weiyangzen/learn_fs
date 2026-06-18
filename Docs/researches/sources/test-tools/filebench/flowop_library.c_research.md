<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/flowop_library.c -->
# sources/test-tools/filebench/flowop_library.c

Purpose: implements Filebench's built-in WML flowops. It supplies the prototype table consumed by `flowoplib_flowinit()` and the execution logic for I/O, file metadata operations, synchronization, rate limiting, finish conditions, delays, printing, and random-variable validation.

Important APIs/functions: `flowoplib_funcs[]` registers names such as `read`, `write`, `openfile`, `createfile`, `closefile`, `deletefile`, `fsync`, `fsyncset`, `makedir`, `removedir`, `listdir`, `statfile`, `readwholefile`, `writewholefile`, `appendfile`, `appendfilerand`, `block`, `wakeup`, `semblock`, `sempost`, `eventlimit`, `bwlimit`, `iopslimit`, `opslimit`, `finishoncount`, `finishonbytes`, `hog`, `delay`, `print`, and `testrandvar`. Public `flowoplib_iosetup()` composes fd selection/opening, working-set discovery, and buffer allocation/alignment.

Control flow: each flowop resolves the needed fd with `flowoplib_fdnum()`, may select a `filesetentry_t` through `fileset_pick()`, performs plugin-dispatched filesystem calls through `FB_*` macros, wraps measured work in `flowop_beginop()`/`flowop_endop()`, and returns Filebench status codes. Rate limiters consume eventgen queue credits based on global or target flowop stats. Semaphore flowops use System V semaphores when available, otherwise POSIX semaphores. Finish flowops return `FILEBENCH_NORSC` when thresholds are reached.

State/persistence: thread fd arrays (`tf_fd`, `tf_fse`, `tf_fdrotor`) carry open file state between flowops. Fileset entries track existence, busy state, open counts, and idle counters. `fo_buf` is resized lazily for private buffers; `tf_mem` is used for random I/O buffer offsets. `fo_targets`, `fo_tputbucket`, and `fo_tputlast` cache target and limiter state.

Dependencies/integration: depends on `flowop.c` timing/stat helpers, `fileset` allocation/open/unbusy, random helpers, eventgen shared state, IPC locks/semaphores, filesystem plugin vector, and platform flags for direct I/O, fadvise, semtimedop, and System V semaphores.

Risks: several paths ignore return values from filesystem calls such as unlink/mkdir/rmdir/fsync, so benchmark state may diverge from storage reality. The fd and fileset invariants are strict; opening twice, closing closed fds, raw-device misuse, or conflicting fd/fileset names abort or error. Direct I/O alignment is hand-rolled. Event and semaphore flowops can block indefinitely or for long timeouts if paired targets are missing or eventgen stops unexpectedly. `flowoplib_read()` calls `flowop_endop()` twice on read error in one branch.

Test signals: WML coverage should exercise every registered flowop, fd rotation, raw device/open flags, random/sequential read/write offsets, no-resource fileset exhaustion, event rate limiting, semblock/sempost pairing, finish conditions, and teardown of `testrandvar` private state.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/flowop_library.c -->
