# sources/test-tools/strace/bundled/linux/include/uapi/linux/loop.h

Purpose: declares the loop block device ioctl ABI for attaching backing files, configuring flags, querying status, resizing capacity, direct I/O, block size, and loop-control device operations.

Important APIs/types/functions: `loop_info` is the legacy status layout; `loop_info64` is the modern layout; `loop_config` atomically combines backing fd, block size, and status. Constants include `LO_FLAGS_*`, settable/clearable masks, obsolete crypto IDs, `LOOP_*` ioctls, and `/dev/loop-control` ioctls.

Control flow: userspace finds or creates a loop device, calls `LOOP_SET_FD` or `LOOP_CONFIGURE`, adjusts status or capacity, optionally changes backing fd, and detaches with `LOOP_CLR_FD`.

State/persistence behavior: ioctls mutate kernel block-device state and backing-file association. `AUTOCLEAR` delays cleanup until last close; read-only, partition scan, and direct-IO flags affect later block operations.

Dependencies/integration: depends on asm posix types and Linux integer types. Integrates with block layer, partition scanning, mount tooling, and `/dev/loop-control`.

Risks and test signals: legacy 32-bit fields, obsolete encryption members, and ioctl numbers without `_IO*` encoding matter for tracing. Tests should decode `loop_info64`, `loop_config`, flag masks, control ioctls, and autoclear lifecycle.
