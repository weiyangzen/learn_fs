# sources/test-tools/strace/bundled/linux/include/uapi/linux/pidfd.h

## Purpose

Defines pidfd-related flags, information structures, and pidfs ioctl numbers. strace uses these constants to decode `pidfd_open`, `pidfd_send_signal`, and pidfd namespace/info ioctls.

## Important APIs, Types, and Dependencies

The header includes `linux/types.h`, `linux/fcntl.h`, and `linux/ioctl.h`. `PIDFD_NONBLOCK` and `PIDFD_THREAD` alias file-open flags; kernel-only aliases expose stale/autokill internal flags. Signal targeting flags are `PIDFD_SIGNAL_THREAD`, `PIDFD_SIGNAL_THREAD_GROUP`, and `PIDFD_SIGNAL_PROCESS_GROUP`. `struct pidfd_info` is versioned by `PIDFD_INFO_SIZE_VER0` through `VER3` and includes a request/result `mask`, cgroup id, pid/tgid/ppid, real/effective/saved/fs credentials, exit code, coredump fields, and supported-mask reporting. `PIDFD_INFO_*` and `PIDFD_COREDUMP_*` bits describe optional sections. `PIDFS_IOCTL_MAGIC` defines namespace getter ioctls and `PIDFD_GET_INFO`.

## Control Flow, State, and Integration

Runtime flow is fd-centered: userspace obtains a pidfd, sends signals or ioctls to query the referenced process, and the kernel snapshots current process metadata. State is intentionally race-prone after return because the target may exit immediately; correctness depends on pidfd identity at the moment the ioctl was serviced.

## Risks and Test Signals

Risks include assuming returned process metadata remains live, reading optional fields without verifying `mask`, using the wrong version size, and conflating thread pidfds with process-group operations. Test signals are decoder coverage for namespace getter ioctl names, `PIDFD_GET_INFO` in/out masks, coredump subfields, and pidfd signal flags.
