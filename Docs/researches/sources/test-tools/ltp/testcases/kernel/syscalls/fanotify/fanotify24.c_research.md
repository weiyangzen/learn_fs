# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify24.c

Purpose: tests fanotify pre-content and permission events, including custom denial errno responses and range information for mmap/read/write access. It also covers open-exec permission behavior and a regression for correct mmap offset propagation.

Important APIs/types/functions: `FAN_CLASS_PRE_CONTENT`, `FAN_PRE_ACCESS`, `FAN_OPEN_PERM`, `FAN_OPEN_EXEC_PERM`, `FAN_RESPONSE_ERRNO`, `fanotify_response`, `fanotify_event_info_range`, `SAFE_MMAP`, `pread`, `pwrite`, `execve`, mark types `INODE`, `MOUNT`, `FILESYSTEM`, and `PARENT`, plus the resource helper `fanotify_child`.

Control flow: setup creates and truncates a watched data file, verifies `FAN_PRE_ACCESS` support, and copies `fanotify_child` into the mounted filesystem. Each case initializes a pre-content fanotify group, marks files or parent/mount/filesystem, forks a child to perform open, mmap, write, read, close, and exec attempts, then the parent reads permission events, validates mask, pid, range count/offset for pre-access events, writes the configured allow/deny response, checks that reading event fds does not recursively generate events, and waits for child status.

State/persistence behavior: the child mutates and maps a test file and attempts to execute a copied helper. Parent-held fanotify queue state controls whether child syscalls proceed and what errno they observe. `fd_notify` is closed from a SIGCHLD handler to stop blocking reads when the child exits.

Dependencies/integration: root and mounted filesystems are required. It depends on kernel support for pre-content events and the resource file `fanotify_child`.

Risks/test signals: timing and blocking behavior are central. Failures show as wrong event masks, pid mismatch, missing range info, wrong count/offset, wrong child errno, failed response write, or bad child exit.
