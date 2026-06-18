# sources/user-network-fs/samba/source3/smbd/smb2_lock.c

Purpose: implements SMB2 byte-range lock/unlock, including multi-lock validation, durable/multichannel lock-sequence replay detection, blocking waits, share-mode watch retries, POSIX/Windows lock flavors, and cancellation.

Important APIs and types: `smbd_smb2_request_process_lock()` decodes the packet. `smbd_smb2_lock_send()` / `smbd_smb2_lock_recv()` run the operation. `struct smbd_smb2_lock_state` stores SMB2/SMB1 request state, fsp, blocking flags, retry/poll intervals, converted lock elements, and lock sequence tracking. `smbd_smb2_lock_try()`, `smbd_smb2_lock_retry()`, cleanup, and cancel helpers manage async behavior.

Control flow: the processor verifies size `0x30`, reads lock count, SMB2.1+ lock sequence, file IDs, and lock entries, permits unlocks despite `NETWORK_SESSION_EXPIRED`, resolves the fsp, and queues execution. The send helper creates fake SMB1 state, enables sequence checking for multichannel or durable handles unless disabled, detects replayed sequence buckets, validates lock flags and blocking rules, converts wire entries to `smbd_lock_element`s with request GUIDs and open persistent IDs, and performs unlocks synchronously. Locks call `share_mode_do_locked_brl()`; retry statuses set timers or share-mode watches, non-blocking conflicts fail, and successful async locks record the sequence value. Cancellation returns `RANGE_NOT_LOCKED` for close/logoff/tree-disconnect cancellation and `CANCELLED` otherwise.

State and persistence: byte-range locks persist in Samba locking/share-mode databases. Sequence replay state is stored in `smbXsrv_open` global lock sequence array. Pending blocking locks live as tevent requests on the fsp async list.

Dependencies and integration: depends on share-mode and byte-range lock helpers, `dbwrap_watch`, generated open-files structures, fake SMB1 glue, loadparm locking settings, `smbXsrv_open`, close/logoff/tdis cancellation, and negotiated multichannel capability.

Risks: mixed lock/unlock flags, multi-lock blocking rules, and replay sequence behavior are protocol-sensitive. POSIX handles differ from Windows handles and reject write locks on read-only POSIX opens. Backend `NT_STATUS_RETRY` can wait indefinitely if not eventually resolved. Cancellation status must reflect closing/session/tree state.

Test signals: cover `smb2.lock`, raw/base lock suites, POSIX timed locks, durable/multichannel sequence buckets, zero count, malformed dynamic entries, expired session unlock, invalid flags, blocking vs fail-immediately, close/logoff cancellation, backend retry timers, and share-mode wakeups.
