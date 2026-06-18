# sources/user-network-fs/samba/source3/smbd/smb2_ioctl.c

Purpose: implements the SMB2 IOCTL/FSCTL front door: wire buffer validation, credit charge, FSCTL-only enforcement, handle requirements, dispatch by device type, and response/error formatting.

Important APIs and types: `smbd_smb2_request_process_ioctl()` decodes and validates requests. `smbd_smb2_ioctl_send()` / `smbd_smb2_ioctl_recv()` wrap dispatch. `struct smbd_smb2_ioctl_state` is shared with device modules. `smbd_smb2_ioctl_is_failure()` classifies allowed data-bearing statuses.

Control flow: the handler verifies body size `0x39`, extracts control code, file IDs, input/output offsets, lengths, max lengths, and flags. It bounds input and output ranges inside the dynamic area, handles zero-length offset quirks, rejects output overlapping before input end, checks uint32 overflow in credit-charge sizing, and requires `SMB2_IOCTL_FLAG_IS_FSCTL`. Handleless FSCTLs require all-ones file IDs; others resolve an fsp. Dispatch uses the device type bits to call DFS, filesystem, named-pipe, network-filesystem, or smbtorture modules. The done callback handles requested disconnect, max-output overflow, allowed error-with-data statuses, optional torture body padding, and the `0x30` IOCTL response.

State and persistence: per-request talloc state. Async IOCTLs against an fsp are registered in the fsp AIO list so close/logoff/tree disconnect can wait or cancel. Submodules may mutate file or connection state.

Dependencies and integration: depends on SMB2 packet helpers, `ntioctl.h`, generated IOCTL NDR, fake SMB1 glue, AIO tracking, and all `smb2_ioctl_*` modules.

Risks: offset/length arithmetic is security-sensitive. Handleless and handle-bound FSCTL distinctions must match the spec. Allowed-status classification is required for pipe/DFS/QAR/copychunk partial responses. Rare body-padding and disconnect paths must be preserved.

Test signals: fuzz offset/length combinations, non-FSCTL flags, handleless controls with real handles, handle-bound controls with all-ones IDs, output overflow, allowed error-with-data, async close behavior, and torture padding.
