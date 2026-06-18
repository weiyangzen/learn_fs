<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_ioctl.c -->
# sources/test-tools/strace/src/pidfd_ioctl.c

Purpose: decodes pidfd-specific ioctl commands, including namespace fd getters and `PIDFD_GET_INFO`.

Important APIs/types/functions: `pidfd_ioctl`, `pidfd_ioctl_is_namespace_fd`, `pidfd_ioctl_is_get_info`, `pidfd_ioctl_print_pidfd_info_fields`, `struct pidfd_info`, `pidfd_info_mask`, and `pidfd_coredump_mask`.

Control flow: namespace ioctls are rendered as fd-returning commands. `PIDFD_GET_INFO` prints the requested mask on entry, stores it in tcb private data if needed, then on exit fetches the structure, notes mask changes, and conditionally prints fields gated by returned mask bits and user-provided size.

State and persistence behavior: per-ioctl requested mask is stored in tcb private data or private ulong across enter/exit. No global state.

Dependencies and integration points: used by generic ioctl dispatch; depends on `<linux/pidfd.h>`, pid/uid/signal/wait-status printers, and xlat tables.

Risks: this is a 2026 kernel-facing area with evolving `pidfd_info` versions. Size and mask gating must match the kernel or fields may be omitted or over-read.

Test signals: all namespace fd ioctls, `PIDFD_GET_INFO` short sizes, each mask bit, changed returned mask, failed exits, coredump fields, credential fields, and supported-mask output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_ioctl.c -->
