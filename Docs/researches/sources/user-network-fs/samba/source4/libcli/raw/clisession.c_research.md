# sources/user-network-fs/samba/source4/libcli/raw/clisession.c

Purpose: manages raw SMB1 session contexts and implements session setup, ulogoff, and exit requests.

Important APIs: `smbcli_session_init()`, `smb_raw_sesssetup_send()`, `smb_raw_sesssetup_recv()`, `smb_raw_sesssetup()`, `smb_raw_ulogoff_send()`, `smb_raw_ulogoff()`, `smb_raw_exit_send()`, and `smb_raw_exit()`.

Control flow: session init references or steals the transport, sets PID, invalid VUID, options, creates an `smbXcli_session`, and derives `flags2` from negotiated capabilities and signing state. Session setup send supports old, NT1, and SPNEGO levels, packing appropriate password/security blobs and strings. Recv accepts success or `MORE_PROCESSING_REQUIRED`, validates word counts, extracts VUID/action, and pulls returned OS/Lanman/domain/workgroup/security blobs.

State and persistence: session object stores transport, PID, VUID, options, `smbXcli` session, and `flags2`. Remote session setup/logoff affects server-side authenticated state.

Dependencies and integration: uses raw request helpers, SMBX client base session, filesystem PID, and negotiated transport state.

Risks: SMB2 session setup level is explicitly unsupported. String pull parsing depends on response layout and word count validation. VUID is still kept for legacy callers while `smbXcli` is the future path. Test signals include old/NT1/SPNEGO setup, multi-step SPNEGO `MORE_PROCESSING_REQUIRED`, signing flag propagation, ulogoff/exit, invalid level handling, and malformed response data.
