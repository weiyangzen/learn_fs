# sources/test-tools/strace/bundled/linux/include/uapi/linux/seccomp.h

## Purpose

Defines seccomp modes, syscall operations, BPF return encodings, user notification structures, and notification fd ioctls. strace uses it for `seccomp(2)`, `prctl(PR_SET_SECCOMP)`, and notification ioctl decoding.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports `SECCOMP_MODE_DISABLED`, `STRICT`, and `FILTER`; syscall operations `SECCOMP_SET_MODE_STRICT`, `SET_MODE_FILTER`, `GET_ACTION_AVAIL`, and `GET_NOTIF_SIZES`; filter flags including TSYNC, LOG, SPEC_ALLOW, NEW_LISTENER, TSYNC_ESRCH, and WAIT_KILLABLE_RECV; ordered `SECCOMP_RET_*` action values plus masks; `struct seccomp_data`; `struct seccomp_notif_sizes`, `seccomp_notif`, `seccomp_notif_resp`, and `seccomp_notif_addfd`; addfd and continue flags; and `SECCOMP_IOCTL_NOTIF_RECV`, `SEND`, `ID_VALID`, `ADDFD`, and `SET_FLAGS`.

## Control Flow, State, and Integration

Runtime flow is installing a seccomp mode/filter, then optionally receiving user notifications on a listener fd, validating ids, responding, or injecting fds into the target. State is task/thread-group seccomp filter stacks and live notification ids. The header documents that `CONTINUE` is not a general security policy mechanism because intercepted syscall arguments can change while blocked.

## Risks and Test Signals

Risks include action ordering mistakes, masking the high action bits incorrectly, unsafe assumptions about notification TOCTOU, and missing newer listener/addfd flags. Test signals include named `SECCOMP_RET_*` decoding, `seccomp_data` argument layout, notification ioctl structs, and composed filter flag output.
