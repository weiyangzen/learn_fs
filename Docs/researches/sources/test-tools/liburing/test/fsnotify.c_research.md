<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fsnotify.c -->
## sources/test-tools/liburing/test/fsnotify.c

Purpose: verifies io_uring O_DIRECT reads still generate fanotify access events with a meaningful task pid.

Important APIs/types/functions: conditional `CONFIG_HAVE_FANOTIFY`, `fanotify_init`, `fanotify_mark`, `io_uring_prep_read`, `fork`, `wait`, and `O_DIRECT`.

Control flow: when fanotify is available, the test creates or opens a regular file with O_DIRECT, marks it for `FAN_ACCESS | FAN_MODIFY`, forks, and the parent performs an io_uring read. The child reads one fanotify event and fails if the access mask is missing or the pid is zero.

State and persistence behavior: fanotify fd watches the target file while the read request completes. Temporary `.fsnotify.*` file is removed on exit.

Dependencies and integration points: requires fanotify permissions, regular files, O_DIRECT support, and io_uring read attribution to task context.

Risks: skipped without fanotify or privilege. Parent/child synchronization relies on fanotify blocking until the read event exists.

Test signals: pass means direct io_uring reads trigger fsnotify access events tied to a userspace task.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fsnotify.c -->
