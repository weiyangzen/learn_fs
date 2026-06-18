# sources/user-network-fs/samba/source4/torture/ntp/ntp_signd.c

Purpose: This file tests Samba's NTP signing daemon protocol over its Unix domain socket and cross-checks the daemon's signature output against Netlogon-derived machine-account credentials.

Important APIs, types, and functions: `struct signd_client_state` stores local/remote socket addresses, a `tstream_context`, send queue, request header/iovecs, reply blob, and status. `test_ntp_signd()` performs the full integration test. `torture_ntp_init()` registers an `ntp` suite with a machine workstation RPC test case against the Netlogon interface.

Control flow: The test obtains the machine workstation name and NT hash, runs `netr_ServerReqChallenge`, initializes Netlogon credential state with AES-capable flags, and authenticates with `netr_ServerAuthenticate3`. It builds an NDR `sign_request` for `SIGN_TO_CLIENT`, connects to `lpcfg_ntp_signd_socket_directory()/socket`, writes a 4-byte length plus NDR request through `tstream_writev_queue_send`, reads a PDU with `tstream_read_pdu_blob_send`, decodes `signed_reply`, and checks protocol version, packet id, success opcode, signed packet length, RID placement, and MD5 signature bytes.

State and persistence behavior: The test creates no files but requires a working machine account, Netlogon secure-channel state, and a live `ntp_signd` Unix socket. It allocates transient talloc memory and mutates the reply blob pointer to skip the length header.

Dependencies and integration points: It depends on tevent, tstream/tsocket, generated Netlogon and ntp_signd NDR, Samba credential helpers, `torture_suite_add_machine_workstation_rpc_iface_tcase()`, and GnuTLS MD5 hashing.

Risks: This is environment-sensitive: missing socket directory, disabled ntp_signd, machine-account setup failure, Netlogon negotiation changes, or crypto behavior changes can fail the test. The manual `reply.data += 4` adjustment is local pointer mutation that assumes the read PDU includes the length header.

Test signals: Success proves the daemon accepts the length-prefixed NDR request, locates the RID/key, signs the packet with the expected machine password hash algorithm, and returns a protocol-conformant reply.
