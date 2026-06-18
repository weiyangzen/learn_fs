# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/net_help.c

Implementation of network helper functions, DNS address utilities, TLS/OpenSSL setup, socket portability helpers, and hex conversion.

Key globals:
- `EDNS_ADVERTISED_SIZE = 4096`
- `MINIMAL_RESPONSES = 0`
- `RRSET_ROUNDROBIN = 1`
- `LOG_TAG_QUERYREPLY = 0`
- TLS session ticket key array under `HAVE_SSL`.

Address and socket helpers:
- `str_is_ip6`: checks for `:`.
- `fd_set_nonblock` / `fd_set_block`: uses `fcntl` or Windows `ioctlsocket`.
- `is_pow2`: treats 0 as true.
- `memdup`: malloc/copy helper.
- `log_addr`, `log_name_addr`, `log_err_addr`: formatted address diagnostics.
- `extstrtoaddr`: parses IP strings with optional `@port`.
- `ipstrtoaddr`: parses IPv4/IPv6, including IPv6 `%scope`.
- `netblockstrtoaddr`: parses `ip/prefix`, validates prefix, masks host bits.
- RPZ helpers:
  - internal `ipdnametoaddr`
  - `netblockdnametoaddr`
- Auth-name parsing:
  - `authextstrtoaddr`: parses IP with optional `@port` and `#tls-auth-name`.
  - `authextstrtodname`: parses domain with optional port/auth name into wire-format dname.
- `sockaddr_store_port`: writes port into IPv4/IPv6 sockaddr.
- DNS query logging:
  - `log_nametypeclass`
  - `log_query_in`
- Sockaddr comparison:
  - `sockaddr_cmp`: address plus port.
  - `sockaddr_cmp_addr`: address only.
  - `sockaddr_cmp_scopeid`: address plus port plus IPv6 scope ID.
- Address predicates/manipulation:
  - `addr_is_ip6`
  - `addr_mask`
  - `addr_in_common`
  - `addr_to_str`
  - `prefixnet_is_nat64`
  - `addr_to_nat64`
  - `addr_is_ip4mapped`
  - `addr_is_ip6linklocal`
  - `addr_is_broadcast`
  - `addr_is_any`
- `sock_list_insert`, `sock_list_prepend`, `sock_list_find`, `sock_list_merge`: regional linked-list utilities for socket origins/blacklists.

Crypto/TLS helpers:
- `log_crypto_err`, `log_crypto_err_code`, `log_crypto_err_io`, `log_crypto_err_io_code`: OpenSSL error reporting with fallbacks when SSL is absent.
- `log_cert`: verbose X509 certificate printing.
- ALPN callbacks:
  - DoT selects `dot`.
  - DoH uses nghttp2 protocol selection when available.
- `listen_sslctx_setup`: disables legacy protocols, optionally disables TLS 1.2/1.3 based on config, disables renegotiation when supported, sets cipher preference, handles OpenSSL 3 unexpected EOF option, and may set security level to 0.
- `listen_sslctx_setup_2`: enables ECDHE setup where needed.
- `listen_sslctx_create`: creates server SSL context, loads certificate/key, optional client CA verification, ciphers/ciphersuites, ticket callback, and ALPN.
- Windows trust-store support through `add_WIN_cacerts_to_openssl_store`.
- `connect_sslctx_create`: creates client SSL context, disables legacy protocols, optionally loads client cert/key and CA/default verification paths.
- `incoming_ssl_fd` / `outgoing_ssl_fd`: wrap accepted/connected fd in SSL object and set accept/connect state.
- `check_auth_name_for_ssl` and `set_auth_name_on_ssl`: enforce or configure TLS hostname authentication and SNI.
- Pre-OpenSSL-1.1 lock callbacks:
  - `ub_openssl_lock_init`
  - `ub_openssl_lock_delete`
- TLS ticket key support:
  - `listen_sslctx_setup_ticket_keys`: reads configured 80-byte key files, respecting chroot prefix stripping.
  - `tls_session_ticket_key_cb`: encrypt/decrypt callback using AES-256-CBC and SHA-256 HMAC/MAC APIs.
  - `listen_sslctx_delete_ticket_keys`: wipes and frees key material.

Portability and conversion:
- `sock_strerror`: `strerror` or `wsa_strerror`.
- `sock_close`: `close` or `closesocket`.
- `hex_ntop`: binary to lowercase hex.
- `hex_pton`: hex string to binary with validation.

Research notes:
- The file is heavily conditional around SSL, OpenSSL version/API variants, Windows, nghttp2, and platform socket features.
- NAT64 prefix lengths are restricted to RFC-compatible byte-aligned forms: 32, 40, 48, 56, 64, and 96.
- TLS ticket setup allocates the key array before reading all files; failure paths return early after logging but do not centrally unwind already stored keys in this function.
