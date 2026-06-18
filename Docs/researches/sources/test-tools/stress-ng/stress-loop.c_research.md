# sources/test-tools/stress-ng/stress-loop.c

Purpose: implements `loop`, a privileged Linux loopback-device stressor. It creates backing files, attaches them to `/dev/loop*`, and exercises loop ioctls, sysfs attributes, mmap I/O, direct I/O, status changes, capacity changes, and invalid ioctl paths.

Important APIs/types/functions: `stress_loop_supported()` requires `CAP_SYS_ADMIN`. `stress_loop()` owns the lifecycle and uses `/dev/loop-control` ioctls such as `LOOP_CTL_ADD`, `LOOP_CTL_GET_FREE`, `LOOP_CTL_REMOVE`, plus device ioctls such as `LOOP_SET_FD`, `LOOP_CLR_FD`, status, capacity, block-size, direct-I/O, change-fd, and configure commands.

Control flow: the stressor creates an unlinked backing file of `loop-bytes`, synchronizes, then repeatedly obtains or creates a loop device, opens it, attempts invalid and valid backing fd association, reads sysfs loop attributes, writes/reads data, maps the loop device, applies status/flag operations, tests resize/block-size/direct-I/O/change-fd/configure paths, clears association, removes the loop device, and increments bogo ops.

State and persistence: temporary backing files are unlinked early and directories are removed at exit. Kernel loop devices are removed with retries to handle `EBUSY`. Memory usage is reported from configured backing size.

Dependencies/integration: gated by `linux/loop.h` and loop ioctl constants. Integrates with capability checks, temp-file helpers, mincore/mmap helpers, memory accounting, and `VERIFY_ALWAYS`.

Risks/test signals: requires root-like privileges and mutates kernel loop-device state. Useful signals are skip without `CAP_SYS_ADMIN`, successful attach/detach/remove, no leaked loop devices, valid `EBUSY` retry handling, and bogo increments after lifecycle passes.
