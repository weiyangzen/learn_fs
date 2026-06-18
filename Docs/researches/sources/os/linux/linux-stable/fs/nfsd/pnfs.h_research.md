# File Research: sources/os/linux/linux-stable/fs/nfsd/pnfs.h

## Summary
NFSD pNFS layout interface header.

## Contents
Defines pNFS device-id mapping, the `nfsd4_layout_ops` operation table, layout/device preprocessing declarations, layout insertion/return helpers, device-id helpers, and pNFS lifecycle functions. It declares block, SCSI, and flex-file layout operation providers when their configs are enabled.

## Important Details
`nfsd4_layout_ops` abstracts layoutget, getdeviceinfo, layoutcommit, encoding, client fencing, recall behavior, and notification capabilities. When `CONFIG_NFSD_PNFS` is disabled, setup/return/close/init/exit functions compile to no-ops.

## Risks
This header is the contract between NFSv4 state handling and layout-specific implementations. Layout stateids, device IDs, recalls, and fencing must agree across `state.h`, layout modules, and XDR encoding. Stub behavior must remain safe for kernels with NFSv4 but no pNFS.
