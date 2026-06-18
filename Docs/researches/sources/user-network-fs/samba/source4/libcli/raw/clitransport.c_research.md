# sources/user-network-fs/samba/source4/libcli/raw/clitransport.c

Purpose: manages raw SMB1 transport state over an established socket/SMBX connection, including capabilities, request submission/completion, oplock break reception, idle callbacks, and echo.

Important APIs: `smbcli_transport_init()`, `smbcli_transport_raw_init()`, `smbcli_transport_dead()`, `smbcli_transport_idle_handler()`, `smbcli_transport_process()`, `smbcli_transport_setup_subreq()`, `smbcli_transport_send()`, `smb_raw_echo_send()`, `smb_raw_echo_recv()`, and `smb_raw_echo()`.

Control flow: init clamps protocol to NT1, builds SMB1 capability flags from options, and creates an `smbXcli_conn`. Request send converts an old `smbcli_request` into an `smb1cli_req`, optionally creates a pending break listener when an oplock handler exists, submits the chain, and marks request state receive/error. Completion receives headers/words/bytes, validates contiguous iovec layout, fills the request input buffer, updates transport last-error state, marks done, and runs async callback. Break handler receives MID `0xFFFF` packets, re-arms itself, extracts TID/FNUM/level, and calls the oplock handler.

State and persistence: transport stores event context, options, SMBX connection, idle timer, last error, break subrequest, and oplock callback. No local persistence; remote echo/oplock behavior affects protocol state.

Dependencies and integration: uses tevent, socket/read SMB helpers, NBT definitions, SMBX base APIs, raw request structures, and `clioplock.c` callbacks.

Risks: SMB2+ is clamped away. Transport death normalizes generic statuses and disconnects the SMBX connection. The iovec contiguity check protects legacy buffer assumptions and is a key regression point. Break listener setup is tied to outgoing request submission, so idle connections with newly installed handlers may not listen until a request is sent. Test signals include capability flag construction, raw init from existing SMBX connection, request success/error, socket error without recv iov, oplock break rearming, idle handler cancellation, echo repeat handling, and `smbcli_transport_process()` nonblocking loop behavior.
