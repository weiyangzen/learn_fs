<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_mnt_get.c -->
# sources/test-tools/strace/tests/ioctl_nsfs-ns_mnt_get.c

Purpose: tests mount namespace id ioctls `NS_MNT_GET_INFO`, `NS_MNT_GET_NEXT`, and `NS_MNT_GET_PREV`.

Important APIs/types/functions: Uses `/proc/self/ns/mnt`, `linux/nsfs.h`, `linux/ioctl.h`, `struct mnt_ns_info`, `uint64_t` namespace ids, and `ioctl` command variants for mount namespace information and traversal.

Control flow: probes invalid fd and bad pointers, opens the current mount namespace, calls info/next/prev commands with crafted or real buffers, prints successful namespace ids or fallback error strings, and closes the fd.

State and persistence behavior: reads namespace metadata only; no persistent changes. Output state is the current mount namespace id and related traversal result if the kernel supports the ioctls.

Dependencies/integration points: depends on `/proc/self/ns/mnt`, nsfs UAPI availability, and strace decoding of nested namespace-id structs.

Risks and test signals: kernel support for these newer ioctls may vary. Passing output confirms correct command naming, pointer handling, id formatting, and graceful behavior on unsupported kernels.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_mnt_get.c -->
