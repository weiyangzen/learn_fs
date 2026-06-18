# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/net_help.h

Public interface for network helper functions and constants.

Key constants/macros:
- DNS flag bits in host byte order:
  - `BIT_CD`, `BIT_AD`, `BIT_Z`, `BIT_RA`, `BIT_RD`, `BIT_TC`, `BIT_AA`, `BIT_QR`
  - `FLAGS_GET_RCODE`, `FLAGS_SET_RCODE`
- `UDP_AUTH_QUERY_TIMEOUT 3000`
- EDNS:
  - `EDNS_ADVERTISED_VERSION 0`
  - extern `EDNS_ADVERTISED_SIZE`
  - `EDNS_DO`
- Address sizes:
  - `INET_SIZE 4`
  - `INET6_SIZE 16`
- DNSKEY flags:
  - `DNSKEY_BIT_ZSK`
  - `DNSKEY_BIT_SEP`
- `GET_RANDOM_ID(rnd)`
- fallback `MSG_DONTWAIT 0`
- extern config-style globals:
  - `MINIMAL_RESPONSES`
  - `RRSET_ROUNDROBIN`
  - `LOG_TAG_QUERYREPLY`

Declared API groups:
- Generic helpers:
  - IP-family detection, nonblocking/blocking fd setup, power-of-two check, `memdup`.
- Logging helpers:
  - address logging, name/address logging, errno/address logging, name/type/class logging, query logging.
- Parsing/conversion:
  - `extstrtoaddr`
  - `ipstrtoaddr`
  - `netblockstrtoaddr`
  - `authextstrtoaddr`
  - `authextstrtodname`
  - `sockaddr_store_port`
  - `addr_to_str`
  - `netblockdnametoaddr`
- Address comparison/predicates:
  - `sockaddr_cmp`
  - `sockaddr_cmp_addr`
  - `sockaddr_cmp_scopeid`
  - `addr_is_ip6`
  - `addr_mask`
  - `addr_in_common`
  - `prefixnet_is_nat64`
  - `addr_to_nat64`
  - `addr_is_ip4mapped`
  - `addr_is_ip6linklocal`
  - `addr_is_broadcast`
  - `addr_is_any`
- `sock_list` operations:
  - insert, prepend, find, merge.
- Crypto/TLS interface:
  - OpenSSL error logging.
  - certificate logging.
  - listening/client SSL context creation and setup.
  - SSL fd wrapping.
  - TLS auth-name checking/SNI/hostname setup.
  - OpenSSL lock initialization/deletion.
  - TLS session ticket key setup/deletion.
- Socket portability:
  - `sock_strerror`
  - `sock_close`
- Hex conversion:
  - `hex_ntop`
  - `hex_pton`

Research notes:
- This header ties together low-level socket handling, DNS wire/log formatting, EDNS sizing, NAT64 conversion, TLS setup, and portability glue.
- It is a broad utility surface; changes here affect config parsing, outbound networking, listener TLS setup, logging, and DNS module code.
