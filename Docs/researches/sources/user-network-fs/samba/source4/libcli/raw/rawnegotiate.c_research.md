<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawnegotiate.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawnegotiate.c

Purpose: `rawnegotiate.c` manages SMB1 raw client protocol negotiation and populates the raw transport's negotiated capability cache from the lower-level `smbXcli` connection.

Important APIs, types, and functions: Entry points are `smb_raw_negotiate_fill_transport`, `smb_raw_negotiate_send`, `smb_raw_negotiate_recv`, and `smb_raw_negotiate`. The async state is `smb_raw_negotiate_state`. The code delegates network negotiation to `smbXcli_negprot_send/recv` and reads results with `smbXcli_conn_protocol`, `smb1cli_conn_server_security_mode`, `smbXcli_conn_max_requests`, `smb1cli_conn_max_xmit`, capability/session key/security blob/challenge/time helpers, and braw/lockread capability helpers.

Control flow: The async send function clamps `maxprotocol` to `PROTOCOL_NT1`, normalizes `minprotocol`, creates a tevent request, starts `smbXcli_negprot_send`, and registers `smb_raw_negotiate_done`. The callback receives lower-level status, fills `transport->negotiate`, and completes the request. The sync wrapper polls the tevent request and returns the final NT status.

State and persistence behavior: This file mutates `transport->negotiate`: protocol, security mode, max mux/xmit, session key, capabilities, server time/zone, security blob/challenge, and raw read/write/lockread support bits. That state is then used by request encoders for Unicode selection, large reads/writes, timestamps, and authentication/session setup.

Dependencies and integration points: It depends on tevent, `smbXcli_base`, time conversion, and tevent NTSTATUS helpers. It is used during client connect paths (`cliconnect`, composite connect, transport setup) before session/tree operations are attempted.

Risks: `smb_raw_negotiate_fill_transport` assigns `smb1cli_conn_server_writebraw(c)` into `n->readbraw_supported` instead of `n->writebraw_supported`, leaving write-braw state unset and potentially overwriting read-braw capability. The function rejects protocols above NT1 because this raw layer is SMB1-oriented; SMB2 negotiation must use other paths. Security blob ownership is borrowed from the connection, so lifetime depends on `transport->conn`.

Test signals: Basic negotiate torture tests and connection setup tests should assert protocol clamping, extended-security blob vs challenge selection, timezone propagation, and braw/lockread flags. A targeted regression should verify `readbraw_supported` and `writebraw_supported` are filled independently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawnegotiate.c -->
