# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify14.c

Purpose: Negative validation matrix for invalid `fanotify_init()`/`fanotify_mark()` flag and mask combinations, especially with `FAN_REPORT_FID`.

Important APIs/types/functions: `FAN_REPORT_FID`, `FAN_REPORT_NAME`, `FAN_REPORT_TARGET_FID`, dirent event masks, `FAN_MARK_ONLYDIR`, `FAN_MARK_IGNORE`, anonymous pipes, permission/pre-content event masks, SELinux enforcing detection, and `TST_EXP_FAIL_ARR`.

Control flow: Setup requires fid support, discovers supported init flags, creates a test file and pipes. Each table row either expects `fanotify_init` failure or creates a group and expects `fanotify_mark` to fail with the configured errno; `ENOTDIR` cases also verify the same masks are valid on a directory or filesystem mark.

State and persistence behavior: State is mostly validation inputs: mountpoint/file paths, anonymous pipe fds, SELinux mode, and temporary fanotify groups.

Dependencies and integration points: Requires root, mounted all-filesystems coverage, and fanotify support. Regression tags cover ENOTDIR validation and pipe mark rejection.

Risks and test signals: SELinux may produce `EACCES`, so expected errno arrays include it when enforcing. The large table must track evolving fanotify API rules.
