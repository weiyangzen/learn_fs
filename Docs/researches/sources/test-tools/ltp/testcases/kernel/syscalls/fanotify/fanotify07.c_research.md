# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify07.c

Purpose: Checks permission-event cleanup when a fanotify instance is destroyed while children are waiting for responses.

Important APIs/types/functions: `FAN_ACCESS_PERM`, `FAN_CLASS_CONTENT`, `SAFE_FORK`, `SAFE_KILL`, `struct fanotify_response`, `SAFE_CLOSE(fd_notify)`, and raw child management.

Control flow: The test starts children that repeatedly access a watched file, responds to only some permission events, opens a new fanotify instance, closes the original instance with unanswered events, and then stops/reaps children.

State and persistence behavior: State is a permission-event wait queue with some unresolved events plus blocked child processes.

Dependencies and integration points: Requires root and tmpdir; tagged comments reference kernel crash/hang fixes.

Risks and test signals: The signal is survival without list corruption or hang. The test intentionally leaks responses for several events before instance destruction.
