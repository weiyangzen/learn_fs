<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/socket.c -->
# sources/sync-backup/rsync/socket.c

Purpose: socket and connection management for rsync clients, daemon listeners, proxying, test-time TCP wrappers, and socket option parsing. It centralizes outbound connects, inbound daemon accept loops, and the `RSYNC_CONNECT_PROG` test hook.

Important APIs/types/functions: public entry points include `try_bind_local()`, `open_socket_out()`, `open_socket_out_wrapped()`, `is_a_socket()`, `start_accept_loop()`, and `set_socket_options()`. Internal helpers include `establish_proxy_connection()`, `open_socket_in()`, `sigchld_handler()`, `socketpair_tcp()`, and `sock_exec()`. The `socket_options[]` table maps option names such as `SO_KEEPALIVE`, `TCP_NODELAY`, buffer sizes, and IP TOS choices to `setsockopt()` calls.

Control flow: outbound connections parse `RSYNC_PROXY`, optionally split `USER:PASS@HOST:PORT`, call `getaddrinfo()`, iterate all resolved addresses, optionally bind a local address, apply socket options, enforce an alarm-based connect timeout, and then perform an HTTP CONNECT handshake when proxied. `open_socket_out_wrapped()` expands `%H` in `RSYNC_CONNECT_PROG` and either executes a local socket program or delegates to normal TCP connect. Inbound daemon setup resolves passive addresses, opens as many IPv4/IPv6 sockets as possible, applies reuse and configured options, listens on each fd, and then loops in `select()`, accepting one ready socket and forking a child to run the daemon callback.

State and persistence behavior: the file uses process-level environment (`RSYNC_PROXY`, `RSYNC_CONNECT_PROG`), global config (`bind_address`, `sockopts`, `default_af_hint`, `connect_timeout`, `pid_file_fd`), signal handlers for `SIGALRM` and `SIGCHLD`, and inherited descriptors. It does not persist data itself, but daemon children reopen logs and close inherited listener/pid fds.

Dependencies and integration points: depends on rsync logging/error APIs, `getaddrinfo()`, `getnameinfo()`, TCP/IP headers, `base64_encode()`, `lp_socket_options()`, `lp_listen_backlog()`, `shell_exec()`, and cleanup/error constants. The daemon accept loop integrates with clientserver handling via the callback `fn(fd, fd)`.

Risks: the proxy parser supports only simple colon-delimited credentials and CONNECT targets, so IPv6 proxy literals or colons in credentials are fragile. The connect timeout mutates the global `connect_timeout` to `-1` in the alarm handler. `socketpair_tcp()` is security-sensitive because it creates a loopback listener; it mitigates hijack races by comparing accepted peer and local socket endpoints. Socket option parsing uses `strtok()` on a duplicated string and reports unknown options but continues. Daemon forking requires careful fd closure to avoid pid-file and listener leaks.

Test signals: `RSYNC_CONNECT_PROG` and `sock_exec()` are explicitly for tests that need TCP-like behavior without external network access. Useful coverage includes proxy CONNECT success/failure, bind failures over multiple address families, IPv4/IPv6 listener conflict behavior, option parsing, daemon child reaping, and the anti-hijack peer/local-address check in `socketpair_tcp()`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/socket.c -->
