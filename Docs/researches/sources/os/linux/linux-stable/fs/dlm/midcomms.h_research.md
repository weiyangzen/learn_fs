# File Research: sources/os/linux/linux-stable/fs/dlm/midcomms.h

## Purpose
`midcomms.h` declares the DLM mid-level communications API.

## Exports
- Incoming validation/processing: `dlm_validate_incoming_buffer()`, `dlm_process_incoming_buffer()`.
- Send handle API: `dlm_midcomms_get_mhandle()`, `dlm_midcomms_commit_mhandle()`.
- Node address/version/lifecycle: `dlm_midcomms_addr()`, `dlm_midcomms_version_wait()`, `dlm_midcomms_close()`, `dlm_midcomms_start()`, `dlm_midcomms_stop()`, `dlm_midcomms_init()`, `dlm_midcomms_exit()`, `dlm_midcomms_shutdown()`.
- Membership notifications: `dlm_midcomms_add_member()`, `dlm_midcomms_remove_member()`.
- Retransmit: `dlm_midcomms_unack_msg_resend()`.
- Debugfs state readers and raw send.
- Cache factory: `dlm_midcomms_cache_create()`.

## Notes
`struct midcomms_node` is intentionally opaque outside midcomms/debugfs helper use.
