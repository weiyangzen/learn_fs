# File Research: sources/virtualization/libnbd/lib/uri.c

Implements URI parsing, policy enforcement, connection dispatch, URI reconstruction, and URI-prefix detection.

With libxml2:
- `nbd_unlocked_connect_uri`: async connect plus wait.
- `parse_uri_queries`: decodes query string into name/value pairs, accepting `&` or `;`, CGI-style empty values, and ignoring `=value` entries.
- Recognized schemes: `nbd`, `nbds`, `nbd+unix`, `nbds+unix`, `nbd+vsock`, `nbds+vsock`, `nbd+ssh`, `nbds+ssh`.
- Enforces `scheme://` form and handle policies for allowed transports and TLS mode.
- Query parameters include `socket`, `nbd-port`, `compress`, TLS certificates/PSK/hostname/priority/username/verify-peer.
- Local file parameters require `nbd_set_uri_allow_local_file`.
- TLS priority override requires `nbd_set_uri_allow_tls_priority`.

Transport handling:
- TCP defaults to host `localhost` and port 10809, strips IPv6 literal brackets for `getaddrinfo`.
- Vsock defaults CID to host 2 and port 10809.
- SSH builds `ssh [-C] -p PORT [-o User=...] -- server nc ...`, using either Unix socket or localhost TCP on the remote.

URI reconstruction:
- `nbd_unlocked_get_uri`: reconstructs TCP/sockaddr-based Unix/vsock URIs when enough connection data is available.
- Adds TLS username, export path, TLS query params, and socket param as needed.
- Does not support abstract Unix sockets.

Without libxml2:
- URI connect/get APIs return `ENOTSUP`.

Always available:
- `nbd_unlocked_is_uri`: simple prefix check for supported NBD URI schemes.

Research notes:
- URI parsing is a major policy boundary because it can trigger local file reads for TLS material or SSH command execution.
- `append_query_params` does not escape values itself; it relies on libxml URI saving behavior for final URI creation.
