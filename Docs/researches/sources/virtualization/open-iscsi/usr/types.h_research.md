# File Research: sources/virtualization/open-iscsi/usr/types.h

Purpose: Provides common fixed-width and system type includes plus sparse-style big-endian typedef aliases for userspace code.

Key definitions:
- Includes networking/system integer headers: `netinet/in.h`, `stdint.h`, `sys/types.h`, and `limits.h`.
- Defines `__be16` as `uint16_t` and `__be32` as `uint32_t`.

Implementation notes:
- Comments explain that the `__be` names mirror kernel sparse typechecking conventions even though this userspace header maps them directly to integer types.

Dependencies and interactions:
- Included by IPC, transport, and other protocol-facing headers that share kernel-style type names.

Filesystem/storage relevance:
- Supplies protocol type aliases used around iSCSI and kernel-interface structures.
