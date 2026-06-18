<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/inotify.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/inotify.h

Purpose: vendored Linux inotify interface header used by older LTP syscall tests that need stable inotify constants and structures independent of host libc/kernel headers. It defines the userspace `struct inotify_event`, event masks, helper masks, and, behind `__KERNEL__`, the historical kernel producer/consumer API surface.

Important APIs/types/functions: `struct inotify_event` carries watch descriptor, mask, cookie, name length, and trailing name bytes. Public masks include `IN_ACCESS`, `IN_MODIFY`, `IN_ATTRIB`, close/open/move/create/delete/self events, `IN_UNMOUNT`, `IN_Q_OVERFLOW`, `IN_IGNORED`, flag bits such as `IN_ONLYDIR`, `IN_DONT_FOLLOW`, `IN_MASK_ADD`, `IN_ISDIR`, and `IN_ONESHOT`, plus aggregate `IN_CLOSE`, `IN_MOVE`, and `IN_ALL_EVENTS`. Kernel-only declarations cover `struct inotify_watch`, `struct inotify_operations`, queueing helpers, watch add/remove/find APIs, and CONFIG_INOTIFY stubs returning `-EOPNOTSUPP` where appropriate.

Control flow/state: the userspace portion is declarative. Kernel-only code models reference-counted watch state in `inotify_watch`, with comments documenting handle-list and inode-list locking. When CONFIG_INOTIFY is disabled, inline no-op/error stubs preserve buildability while preventing runtime use.

Dependencies/integration: includes `<linux/types.h>` for fixed-width kernel-style types and, for kernel builds, dcache/fs/list/atomic infrastructure. LTP consumers can compile against exact mask values when probing inotify syscalls.

Risks/test signals: this is a compatibility snapshot; divergence from modern kernel headers can hide newer flags or ABI changes. Its value is constant stability, so audits should compare masks and `struct inotify_event` layout against target kernel UAPI when diagnosing inotify test mismatches.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/inotify.h -->
