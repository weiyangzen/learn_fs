<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawrequest.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawrequest.c

Purpose: `rawrequest.c` is the request buffer and wire helper core for the raw SMB1 client layer. It creates request packets, manages chained requests, sends/receives through the transport, grows packet buffers, appends strings/blobs/data, pulls strings/blobs safely, and converts NTTIME/GUID values.

Important APIs, types, and functions: Key functions include `smb_setup_bufinfo`, `smbcli_request_destroy`, `smbcli_request_setup_transport`, `smbcli_request_setup_session`, `smbcli_request_setup`, `smbcli_chained_request_setup`, `smbcli_chained_advance`, `smbcli_request_send`, `smbcli_request_receive`, `smbcli_request_simple_recv`, `smbcli_request_is_error`, append helpers (`smbcli_req_append_string`, `_string_len`, `_ascii4`, `_blob`, `_bytes`, `_var_block`), pull helpers (`smbcli_req_pull_ascii`, `smbcli_req_pull_string`, `smbcli_req_pull_blob`, `smbcli_raw_pull_data`, blob string variants), and `smbcli_pull/push_nttime` plus GUID helpers.

Control flow: Request setup allocates a talloc request, initializes SMB header fields, VWV/data pointers, flags, IDs, and buffer sizes. Append functions grow allocation/data sections and update BCC. Send delegates to transport; receive pumps the tevent loop until the request leaves `RECV`. Chained setup creates a secondary low-level subrequest and rebuilds the output buffer at the chained offset; chained advance receives the second reply and repopulates `req->in`. Pull helpers use `request_bufinfo` for bounds, Unicode alignment, negotiated string mode, and conversion.

State and persistence behavior: State is per-request: packet buffers, pointers into buffers, status, subrequests, flags2, session/tree/transport links, and async metadata. No durable filesystem state is stored. Talloc ownership is central; request destruction frees all child buffers unless `do_not_free` is set.

Dependencies and integration points: This file underpins nearly every raw SMB1 implementation. It depends on tevent, smbXcli low-level request functions, string conversion, NDR GUID routines, request buffer definitions, and transport helpers. Chained open/read, trans2, nttrans, metadata, search, and IOCTL code all rely on these helpers.

Risks: Buffer growth can reallocate and invalidate external local pointers; the code updates request-owned pointers but callers must not cache old ones. `smbcli_req_pull_ascii` returns converted byte size rather than consumed wire bytes, unlike some parser expectations. Bounds checks are careful about wraparound in `smbcli_req_data_oob`, but many higher-level parsers must still validate offsets before calling. Sync receive can loop indefinitely if transport state never advances except for tevent errors/timeouts.

Test signals: Broad raw torture coverage exercises this file indirectly. Focused tests should cover packet growth, Unicode alignment, ASCII/Unicode string pull/push, chained request setup/advance, malformed offsets, zero-length blobs, request destruction with `NULL` and `do_not_free`, GUID round-trips, and transport errors mapped into request status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawrequest.c -->
