# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify17.c

Purpose: checks enforcement of fanotify group and mark limits globally and inside user namespaces. It verifies `EMFILE` when group limits are hit and `ENOSPC` when mark limits are hit, including per-user-namespace limit overrides when supported.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `unshare(CLONE_NEWUSER)`, proc/sys files such as `PATH_FS_MAX_USER_GROUPS`, `PATH_FS_MAX_USER_MARKS`, `PATH_USER_MAX_FANOTIFY_GROUPS`, `PATH_USER_MAX_FANOTIFY_MARKS`, `PATH_USER_MAX_USER_NAMESPACES`, `SAFE_FILE_SCANF`, `SAFE_FILE_PRINTF`, and `setrlimit(RLIMIT_NOFILE)`.

Control flow: `setup()` creates the watched file, verifies fanotify support, records and temporarily raises `max_user_namespaces`, reads current global fanotify limits if available, and raises the open-file limit. Each test forks a child; the child optionally unshares a user namespace and maps uid 0, optionally lowers namespace-local group or mark limits, then loops creating groups and marks until the expected limit error occurs.

State/persistence behavior: modifies proc/sys namespace knobs and restores `max_user_namespaces` in cleanup. It intentionally leaks fanotify fds inside the child because process exit releases them, making limit accounting the state under test rather than long-lived resources.

Dependencies/integration: root is required for namespace/sysctl manipulation. Older kernels without per-user fanotify limits or namespace fanotify support are handled by fallback defaults and `TCONF`.

Risks/test signals: depends on writable proc/sys limit files and enough `RLIMIT_NOFILE`. Passing signals are limit-specific `TPASS` messages; unexpected `EPERM`, unexpected errno, or ability to create beyond the configured limit indicates a kernel or environment mismatch.
