# sources/sync-backup/rsync/clientname.c

Purpose: obtains and validates daemon client IP/hostname, including HAProxy PROXY protocol support.

Important APIs/types/functions: public `client_addr()`, `client_name()`, and `read_proxy_protocol_header()`; helpers `client_sockaddr()`, `compare_addrinfo_sockaddr()`, `check_name()`, and `valid_ipaddr()`.

Control flow: client address uses PROXY-provided address when present, else `getpeername` and `getnameinfo`. `read_proxy_protocol_header()` parses PROXY v2 binary headers and v1 text headers, validates source/destination addresses and ports, and stores source IP. Hostname lookup performs reverse DNS then forward-confirmation to reduce spoofing. IPv4-mapped IPv6 sockets are normalized.

State and persistence: static `ipaddr_buf` stores the current client IP string; no persistent state.

Dependencies/integration: daemon accept/auth/access-control paths use this before host allow/deny and logging. Depends on socket APIs, DNS APIs, rsync IO readers, and cleanup exits.

Risks: PROXY parsing reads from the connection before normal protocol handling; malformed headers must fail closed. DNS validation is security-sensitive and can be slow or unreliable.

Test signals: daemon TCP tests, proxy protocol tests, and CI network runs exercise the path.
