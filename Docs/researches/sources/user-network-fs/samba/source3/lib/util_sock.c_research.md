# sources/user-network-fs/samba/source3/lib/util_sock.c

## Purpose
`util_sock.c` is the source3 socket utility layer for blocking and async socket setup, SMB packet-length reads, peer-name resolution, Unix-domain pipe socket creation, local-name detection, and small poll wrappers. It bridges POSIX sockets, Samba `tevent`, `tsocket`, interface discovery, memcache, and SMB packet conventions.

## Important APIs and Functions
Key exported entry points are `is_a_socket`, `read_fd_with_timeout`, `read_data_ntstatus`, `read_smb_length_return_keepalive`, `receive_smb_raw`, `open_socket_in_protocol`, `open_socket_in`, `open_socket_out_send`, `open_socket_out_recv`, `open_socket_out`, `get_peer_addr`, `get_remote_hostname`, `create_pipe_sock`, `get_mydnsfullname`, `is_myname_or_ipaddr`, `poll_one_fd`, and `poll_intr_one_fd`. `struct open_socket_out_state` owns the async connect fd, address, timeout, and cleanup callback. `struct name_addr_pair` is a singleton memcache value pairing a `sockaddr_storage` with a resolved remote name.

## Control Flow and Behavior
Read helpers either loop on `sys_read` until a minimum byte count is met or use `poll_intr_one_fd` with a millisecond timeout before each read. SMB receive first reads the 4-byte NetBIOS Session Service length, preserves keepalive behavior, validates the payload length against the caller buffer, optionally caps reads at `maxlen`, and writes a trailing zero word to reduce unterminated string hazards in older callers. Incoming socket setup normalizes address length, sets port, opens the requested socket type/protocol, applies `SO_REUSEADDR`, optionally `SO_REUSEPORT`, forces IPv6-only sockets where available, and binds. Outgoing connects are async: `open_socket_out_send` creates a TCP socket, sets an end time, calls `async_connect_send`, and `open_socket_out_connected` maps connect errors to NTSTATUS; the sync wrapper drives that request on a temporary event context.

## State and Persistence
This file has no durable storage, but it uses process singleton memcache for `get_peer_name` and `get_mydnsfullname` results. `create_pipe_sock` creates filesystem state by ensuring a protected socket directory, unlinking any previous socket path, and binding a Unix-domain socket. `open_socket_out_cleanup` owns fd lifetime, closing the fd on failed or canceled requests and transferring ownership only after successful recv.

## Dependencies and Integration Points
It depends on Samba socket helpers (`samba_sockaddr_set_port`, `print_sockaddr`, `sockaddr_equal`), `tevent`, `async_sock`, `tsocket`, `memcache`, loadparm (`lp_hostname_lookups`, `lp_netbios_name`), interface discovery (`get_interfaces`, `ismyaddr`), DNS helpers (`interpret_string_addr_internal`, `sys_getnameinfo`), and SMB length macros. It is used by SMB transport, daemon IPC pipe setup, remote client logging, name matching, and AD/Kerberos or LDAP connection code needing socket primitives.

## Risks and Edge Cases
Timeout reads on disk files can spin because poll/select always reports readiness; the comment explicitly warns about `mincnt` larger than file size. `receive_smb_raw` validates `len > buflen` but then truncates to `maxlen`, so callers must understand that `p_len` can be shorter than the NBSS payload. `matchname` rejects DNS reverse/forward mismatches to avoid spoofing but can produce `UNKNOWN` for misconfigured DNS. Unix socket path length uses `strlcpy` and rejects truncation. `get_mydnsfullname` caches canonical names and can become stale if DNS or hostname changes. `is_myname_or_ipaddr` performs DNS lookups for CNAME-like names and can block on resolver behavior.

## Test Signals
Useful tests include read timeout and EOF cases, keepalive and oversized SMB length handling, IPv4/IPv6 bind with `SO_REUSE*`, async connect success/failure/timeouts, Unix socket path length rejection, reverse DNS spoof checks, hostname lookup disabled mode, and `is_myname_or_ipaddr` matches for netbios name, aliases, localhost, loopback, configured interfaces, and DNS-resolved local addresses.
