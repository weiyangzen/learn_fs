<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/connect.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/connect.c

Purpose: implements the SMB1 composite "full connect" operation: socket establishment or existing `smbXcli_conn` adoption, protocol negotiation, optional session setup, and optional tree connect. It exposes async `smb_composite_connect_send`/`recv` plus sync `smb_composite_connect`.

Important APIs and types: `enum connect_stage`, `struct connect_state`, `smb_composite_connect_send`, `smb_composite_connect_recv`, `connect_socket`, `connect_send_negprot`, `connect_send_session`, `connect_session_setup`, `connect_session_setup_anon`, and `connect_tcon`. It depends on raw SMB calls, `smbcli_sock_connect_send`, `smb_raw_negotiate_send`, `smb_composite_sesssetup_send`, `smb_raw_tcon_send`, credentials, NBT called/calling names, resolver context, loadparm, and smbX signing helpers.

Control flow: the state machine advances via three callback adapters: raw SMB request, composite subrequest, and tevent subrequest. New sockets move through socket connect to negprot; existing connections skip directly to session setup. Session setup creates a `smbcli_session` and provisional `smbcli_tree`; if credentials are absent the connection completes without authentication. If `service` is present, a TCONX path of `\\called_name\service` is sent.

State and persistence: all state is talloc-owned by the composite context until `recv`, where the output tree is stolen to the caller. It mutates session `vuid`, tree `tid`, `device`, and `fs_type`. Extended-signature tree responses protect the session key. Anonymous fallback resets `vuid` and `gensec` before retrying.

Risks: malformed inputs such as NULL event context or NULL gensec settings produce parameter errors, but called/service strings still drive network paths. Anonymous fallback can change security semantics and should be observable through `anonymous_fallback_done`. Signing/session-key transitions are security critical. Test signals include successful existing-connection reuse, kerberos-over-IP hostname substitution, failed auth with fallback, no-service connections, and extended signature TCON behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/connect.c -->
