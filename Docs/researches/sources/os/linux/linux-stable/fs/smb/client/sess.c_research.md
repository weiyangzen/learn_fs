# File Research: sources/os/linux/linux-stable/fs/smb/client/sess.c

This file contains generic CIFS session support shared outside the SMB1-only session implementation. Its main areas are SMB3 multichannel session/channel management, NTLMSSP blob construction/parsing, and authentication method selection.

Multichannel responsibilities:
- Tracks whether a session uses a server interface and maps `TCP_Server_Info` channels to session channel indexes.
- Sets and clears per-channel reconnect flags and `in_reconnect` state.
- `cifs_try_adding_channels()` opens secondary channels according to `chan_max`, SMB dialect, server multichannel capability, interface activity, RDMA compatibility, RSS capability, and speed-derived weights.
- `cifs_decrease_secondary_channels()` tears down excess channels, updates interface reference counts and channel counts, marks sockets for reconnect/termination, and trims reconnect bitmasks.
- `cifs_chan_update_iface()` replaces inactive interface bindings and updates the server destination address.

Channel creation:
- `cifs_ses_add_channel()` creates a temporary mount context from the primary session/server, selects the target interface, reuses authentication and dialect settings, creates a TCP session, adds it to `ses->chans`, negotiates protocol, and runs session setup on the new channel.

NTLMSSP responsibilities:
- `decode_ntlmssp_challenge()` validates challenge blobs, checks server flags against signing/encryption requirements, copies the server challenge, and stores target info.
- `build_ntlmssp_negotiate_blob()` and `build_ntlmssp_smb3_negotiate_blob()` build negotiate messages, with the SMB3 variant adding version fields.
- `build_ntlmssp_auth_blob()` builds the authenticate message from the NTLMv2 response, user/domain/workstation strings, and optional key-exchange session key.
- `cifs_security_buffer_from_str()` centralizes UTF-16 security-buffer packing.

Security selection:
- `cifs_select_sectype()` selects RawNTLMSSP, Kerberos/IAKerb, or NTLMv2 depending on negotiated flavor, requested type, server capabilities, and global security flags.

Risk points:
- Multichannel code is lock-sensitive: `chan_lock`, `iface_lock`, and server locks are used with explicit reference-count handoffs.
- NTLMSSP parsing rejects undersized blobs, incorrect signatures/types, unsupported signing requirements, and out-of-bounds target-info offsets.
