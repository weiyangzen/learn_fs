# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify04.c

Purpose: Checks special fanotify mark flags such as `FAN_MARK_ONLYDIR`, `FAN_MARK_DONT_FOLLOW`, and `FAN_MARK_FLUSH`.

Important APIs/types/functions: `fanotify_mark`, `FAN_MARK_ONLYDIR`, `FAN_MARK_DONT_FOLLOW`, `FAN_MARK_FLUSH`, `FAN_OPEN`, `FAN_NONBLOCK`, symlinks, directories, and nonblocking event reads.

Control flow: The test tries valid and invalid `ONLYDIR` marks, verifies no symlink-follow behavior with `DONT_FOLLOW`, adds multiple inode marks, flushes them, and confirms subsequent opens produce no events.

State and persistence behavior: State is a fanotify group, one regular file, one symlink, one directory, and marks that are added/removed/flushed.

Dependencies and integration points: Requires root and a tmpdir; it compiles only when fanotify headers are present.

Risks and test signals: Expected-failure mark calls are as important as event checks. Nonblocking reads distinguish no-event from blocking behavior.
