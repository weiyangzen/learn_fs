# sources/user-network-fs/samba/source4/param/loadparm.c

Purpose: `loadparm.c` provides helper functions that translate Samba loadparm settings into SMB client option structures.

Important APIs, types, and functions: It exports `lpcfg_smbcli_options` and `lpcfg_smbcli_session_options`. These fill `struct smbcli_options` and `struct smbcli_session_options`.

Control flow: `lpcfg_smbcli_options` reads a parametric `libsmb:client_guid`; if absent, it generates a random GUID. It then fills max transmit/mux, SPNEGO, signing, protocol bounds, Unicode, oplocks, SMB2/3 capabilities, credit request, transports, and SMB3 algorithm capabilities from loadparm. `lpcfg_smbcli_session_options` fills LANMAN, NTLMv2, and plaintext auth booleans.

State and persistence behavior: No state is stored by these helpers. The generated client GUID may differ per call unless configured, affecting client identity in negotiation.

Dependencies and integration points: It depends on loadparm getters, raw SMB client structures, SMB2 negotiate context helpers, GUID utilities, and transport/capability parsers. It is built as the `param_options` subsystem.

Risks: Defaults here affect all clients using these helpers. Random GUID fallback can complicate reproducibility. Capability parsing must remain aligned with loadparm option syntax.

Test signals: Tests should verify configured and random client GUID paths, protocol min/max propagation, signing/auth option mapping, transport parsing, and SMB3 capability parsing.
