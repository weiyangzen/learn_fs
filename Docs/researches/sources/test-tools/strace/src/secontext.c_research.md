# sources/test-tools/strace/src/secontext.c

Purpose: implements optional SELinux context annotations for traced processes, file descriptors, and paths.

Important APIs/types/functions: `parse_secontext`, `get_expected_filecontext`, `selinux_getpidcon`, `selinux_getfdcon`, `selinux_getfilecon`, `print_context`, `selinux_printfdcon`, `selinux_printfilecon`, and `selinux_printpidcon`.

Control flow: context printing is gated by `secontext_set`. Path and fd helpers resolve the tracee's procfs view (`/proc/PID/root`, `cwd`, `fd`) before calling libselinux. If mismatch checking is enabled, expected contexts are resolved via a cached `selabel_handle`; output prints actual context and appends `!!expected` when the printable actual and expected portions differ.

State and persistence behavior: caches the SELinux label handle and permanently disables mismatch lookup after `selabel_open` fails once. Allocated contexts are freed with `freecon`; resolved paths and expected contexts are local to a print call.

Dependencies and integration points: depends on libselinux, large-file stat wrappers, number-set qualifier state, procfs path helpers, and output quoting state (`xflag`). Called by path/socket/fd printers where SELinux annotations are requested.

Risks: procfs path resolution races with target filesystem changes and fd reuse. Mismatch checking can be unavailable if SELinux policy database cannot be opened. Relative paths rely on `tcp->last_dirfd`; missing or stale dirfd context can suppress annotations.

Test signals: run with full/type-only contexts, mismatch mode, absolute and relative paths, dirfd paths, fd annotations, process annotations, unavailable procfs entries, and disabled/missing SELinux policy.
