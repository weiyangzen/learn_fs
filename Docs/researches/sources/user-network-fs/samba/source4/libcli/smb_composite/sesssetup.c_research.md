<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/sesssetup.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/sesssetup.c

Purpose: hides the SMB session setup variants behind one composite API, covering pre-NT1, NT1, and extended-security SPNEGO/GENSEC flows.

Important APIs and types: `struct sesssetup_state`, `smb_composite_sesssetup_send`, `smb_composite_sesssetup_recv`, `smb_composite_sesssetup`, `session_setup_old`, `session_setup_nt1`, `session_setup_spnego_restart`, `session_setup_spnego`, `request_handler`, and the two GENSEC update callbacks. Dependencies include raw sesssetup, credentials, NTLM response generation, GENSEC, SMB signing, and smbX session-key APIs.

Control flow: `send` rejects mandatory encryption above desired, rejects Kerberos-required on legacy/non-SPNEGO protocols, and selects the session setup flavor from negotiated protocol and extended-security capability. Old/NT1 paths build password blobs or NTLM challenge responses and send one SMB request. SPNEGO starts GENSEC, feeds the server negotiate blob, sends one or more SMB sesssetup requests as GENSEC returns more tokens, and handles logon failure retry for kerberos/password fallback.

State and persistence: session `vuid`, `os`, `lanman`, `gensec`, signing state, and session key are mutated. Some response requests are retained for caller-side signing checks until the GENSEC session key is known. The destructor frees outstanding SMB requests.

Risks: this is security-critical. Mutual authentication must continue while GENSEC reports `MORE_PROCESSING_REQUIRED` even if the server returns success. Session key activation, anonymous no-signing, password retry, and kerberos fallback are all sensitive. Test signals include legacy LANMAN rejection with required Kerberos, NTLMv2 without SPNEGO invalid parameter path, multi-leg SPNEGO, failed signing verification, wrong-password retry, anonymous setup, and encryption-required rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/sesssetup.c -->
