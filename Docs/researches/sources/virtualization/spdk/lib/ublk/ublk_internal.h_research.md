# File Research: sources/virtualization/spdk/lib/ublk/ublk_internal.h

This internal header defines ublk compatibility constants and the private control API used by the ublk RPC layer.

It includes Linux `ublk_cmd.h`, supplies fallback definitions for newer kernel features such as `UBLK_F_CMD_IOCTL_ENCODE`, `UBLK_F_USER_COPY`, `UBLK_U_CMD_GET_FEATURES`, and user-copy buffer offset/tag/qid layout constants, then defines default queue depth and queue count.

The declared internal APIs cover target creation/destruction, disk start/stop/recovery, device lookup and iteration, and device metadata accessors for ID, bdev name, queue depth, and queue count.

The header keeps kernel-version compatibility details localized so `ublk.c` can compile against older headers while probing actual runtime features from the kernel.
