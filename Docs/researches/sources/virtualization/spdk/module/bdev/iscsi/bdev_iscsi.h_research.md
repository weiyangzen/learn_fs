# File Research: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi.h

## Purpose
Declares the iSCSI bdev module control interface and option structure.

## Main Contents
- `struct spdk_bdev_iscsi_opts` stores timeout seconds and derived timeout poller period.
- Delete and create callback typedefs.
- `create_iscsi_disk()` starts creation of a bdev from a name, iSCSI URL, and initiator IQN.
- `delete_iscsi_disk()` unregisters a named iSCSI bdev.
- `bdev_iscsi_get_opts()` and `bdev_iscsi_set_opts()` manage global module options.

## Dependencies
Includes SPDK bdev declarations.

## Risks and Notes
The warning in the create API is important: credentials embedded in iSCSI URLs can appear in configuration dumps.
