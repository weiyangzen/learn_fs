# File Research: sources/virtualization/spdk/module/bdev/iscsi/bdev_iscsi_rpc.c

## Purpose
Exposes JSON-RPC methods for iSCSI bdev options, creation, and deletion.

## Main Entry Points
- `bdev_iscsi_set_options` updates timeout seconds at startup or runtime.
- `bdev_iscsi_create` decodes name, initiator IQN, and URL, then calls `create_iscsi_disk()`.
- `bdev_iscsi_delete` decodes name and calls `delete_iscsi_disk()`.

## Internal Mechanics
Create completion maps positive libiscsi/SCSI statuses to JSON-RPC invalid-params errors, negative errno values to stringified errors, and success to the created bdev name. Delete completion returns boolean true on success.

## Dependencies
Uses `bdev_iscsi.h`, SPDK JSON-RPC, string/log helpers, and generated RPC autogen contexts.

## Risks and Notes
The options setter contains a branch for `-EPERM`, but the current `bdev_iscsi_set_opts()` implementation always returns zero after updating derived timeout period. Decode failures are reported as JSON-RPC internal errors rather than invalid params.
