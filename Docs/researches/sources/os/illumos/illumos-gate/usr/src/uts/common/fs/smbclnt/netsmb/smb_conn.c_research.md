# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_conn.c

## Purpose
Implements the SMB client connection object hierarchy: global session manager, virtual circuits/sessions, tree shares, file handles, reference counting, object teardown, reconnect invalidation, and zone shutdown handling.

## Key Elements
The common `smb_connobj` layer provides lock-protected use counts, parent/child lists, `SMBO_GONE` lifecycle state, and `co_gone`/`co_free` callbacks. `smb_co_rele` performs the core teardown sequence: mark gone, call the disconnect callback once, unlink from the parent list, free the object, then release the parent hold. `smb_sm_init`, `smb_sm_idle`, and `smb_sm_done` manage the global VC list and prevent module unload while active VCs remain.

VC support includes `smb_vc_create`, `smb_vc_findcreate`, `smb_vc_hold/rele/kill`, transport allocation, state/CV initialization, request-list initialization, credential/session identity copying, and cleanup of transport state, signing keys, session keys, crypto mechanisms, locks, and CVs. VC matching is zone- and owner-scoped and compares server address, user, and domain case-insensitively.

Share support includes `smb_share_findcreate`, `smb_share_create`, `smb_share_tcon`, `smb_share_invalidate`, and share hold/release/kill wrappers. `smb_share_tcon` serializes concurrent tree-connect attempts with `SMBS_RECONNECTING`, waits interruptibly for another thread's tree connect, and invokes SMB1 or SMB2 tree connect depending on the VC. Share teardown shuts down outstanding share requests and sends tree disconnect.

File-handle support creates handles under shares, marks them valid after successful open, records the VC generation used to open them, and closes them during teardown only when still valid for the current share generation. The zone callbacks kill VCs during zone shutdown and report lingering VCs at zone destroy.

## Dependencies
Depends on illumos locks/CVs/zones/credentials, STREAMS transport descriptors, SMB1/SMB2 protocol helpers, `smb_iod` connection teardown, tree connect/disconnect helpers, file close helpers, UTF-8 case-insensitive comparison, and the password/keychain interface for module lifecycle coordination.

## Behavior/Risks
The parent/child reference model is central to preventing use-after-free; callers rely on external holds from device instances or mounted shares rather than per-request VC holds. `SMBO_GONE` blocks new references and ensures disconnect callbacks run once, so lifecycle flag changes are high risk. Share and file-handle generation checks intentionally make handles stale across reconnect because durable handles are not implemented. Zone shutdown kills connections asynchronously; zone destroy only diagnoses references that should already have been released.
