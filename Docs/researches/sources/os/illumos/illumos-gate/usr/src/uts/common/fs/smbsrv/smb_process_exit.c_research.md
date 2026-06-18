# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_process_exit.c

## Purpose

`smb_process_exit.c` implements the legacy SMB `SMB_COM_PROCESS_EXIT` command. The command tells the server a client process id has exited, allowing the server to close files and release locks associated with that SMB PID.

## Main Interfaces

- `smb_pre_process_exit()` starts DTrace accounting.
- `smb_post_process_exit()` finishes DTrace accounting.
- `smb_com_process_exit()` performs UID lookup and closes matching PID resources.

## Behavior And Data Flow

The command has no parameter or data words. `smb_com_process_exit()` looks up `sr->smb_uid`; if no user exists, it still returns an empty success response as the protocol expects limited errors. If the user exists, it gets the user's credential, attempts to look up the request TID, and closes resources for `sr->smb_pid` either within that tree or across the full session when no valid tree is supplied.

## Dependencies

This file depends on session UID lookup, user credentials, session/tree PID close helpers, SMB result encoding, and DTrace probes.

## Notable Invariants And Risks

- This is mainly for old SMB clients and tests; modern LANMAN-era clients typically close resources explicitly.
- Missing UID is not treated as a hard error.
- If a valid TID is present, cleanup is scoped to that tree; otherwise it scans all session trees.
- It relies on lower-level `smb_tree_close_pid()` and `smb_session_close_pid()` to release locks and ofiles correctly.
