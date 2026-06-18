# File Research: sources/virtualization/open-iscsi/usr/version.h

Purpose: Centralizes the userspace iSCSI tools version string requirement and the sysfs path for the kernel iSCSI transport class version.

Key definitions:
- Requires `ISCSI_VERSION_STR` to be defined by the build system; otherwise compilation fails with `#error Must set ISCSI_VERSION_STR`.
- Defines `ISCSI_VERSION_FILE` as `/sys/module/scsi_transport_iscsi/version`.

Implementation notes:
- Comments note that the tools version may differ from kernel version because kernel-side patches can be merged independently.

Dependencies and interactions:
- Used by session reporting code to print userspace version alongside the kernel iSCSI transport class version.

Filesystem/storage relevance:
- Provides version identity for iSCSI tooling and points to the kernel transport-class version exposed through sysfs.
