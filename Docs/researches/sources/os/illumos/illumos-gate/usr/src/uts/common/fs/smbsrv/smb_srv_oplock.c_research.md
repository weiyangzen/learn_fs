# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_srv_oplock.c

Server-level SMB1/SMB2 oplock and SMB2 lease break orchestration. This file sits above the filesystem-level oplock state machine in `smb_cmn_oplock.c`, translating lower-level break indications into asynchronous server work and protocol-specific break messages.

`smb_oplock_ind_break` is the main callback used by FS-level oplock code. It is called while node ofile-list and oplock locks may already be held, so it only validates completion status, takes an oplock-break hold on the `smb_ofile_t`, allocates an `smb_request_t`, populates tree/user/ofile references, records break level and status, updates handle/lease state, and dispatches `smb_oplock_async_break` to the server notify taskq. Special completion statuses update local handle state directly: `STATUS_NEW_HANDLE` calls `smb_oplock_hdl_moved`, and `NT_STATUS_OPLOCK_HANDLE_CLOSED` calls `smb_oplock_hdl_closed`.

`smb_oplock_ind_break_in_ack` handles break indications generated while processing an SMB2 break acknowledgment. When possible, it appends post-work to the current request so the new break is sent only after the ack reply. If that is impossible, it falls back to taskq dispatch on a server session request.

`smb_oplock_async_break` marks the synthetic request active, calls `smb_oplock_send_break`, updates durable-handle NV state if dirty, completes the request, and frees it. `smb_oplock_send_break` chooses SMB2 lease, SMB2 oplock, or SMB1 oplock break output based on `ofile->f_lease` and the oplock dialect.

State updates are centralized in `smb_oplock_hdl_update`, which records `og_breakto`, marks breaks in progress, increments lease epochs when appropriate, and immediately applies non-ack-required breaks. Persistent durable handles are updated when break state changes without an ack requirement.

The wait helpers implement cancellation-aware synchronization. `smb_oplock_wait_ack` waits for a client ack to reduce oplock/lease state to the requested level, logs timeout details, and handles request cancellation states. `smb_oplock_wait_break` waits for all node-level break bits to clear, also with request cancellation support. `smb_oplock_wait_break_fem` is a simplified FEM path without request cancellation plumbing. Tunables define ack and default wait timeouts.
