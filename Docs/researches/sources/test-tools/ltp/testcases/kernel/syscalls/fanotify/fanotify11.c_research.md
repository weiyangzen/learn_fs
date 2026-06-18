# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify11.c

Purpose: Verifies `FAN_REPORT_TID` reports the triggering thread id instead of the thread-group id.

Important APIs/types/functions: `pthread_create`, `gettid()` via `syscall(SYS_gettid)`, `FAN_REPORT_TID`, `FAN_ALL_EVENTS | FAN_EVENT_ON_CHILD`, `SAFE_FILE_PRINTF`, and `SAFE_PTHREAD_JOIN`.

Control flow: The test runs one case without and one with `FAN_REPORT_TID`, marks the tmpdir, spawns a thread that creates a file named with its tid, reads one event, and compares `event.pid` to either tgid or tid.

State and persistence behavior: State is a fanotify group and the thread-created file event. Global `tid` records the worker thread id for comparison.

Dependencies and integration points: Requires pthread build flags from the Makefile, root, tmpdir, and runtime support check for `FAN_REPORT_TID`.

Risks and test signals: The initial info log prints `event.pid` before the event is read, but pass/fail checks occur after reading. Failures indicate pid/tid reporting mismatch.
