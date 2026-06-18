# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dnssec.h

This header declares optional DNSSEC key lookup helpers.

Key contents:
- Includes `libcrypto.h` and `message.h`.
- Prototypes:
  - `dns_get_key`
  - `dns_RSA_dns_to_x509`
- Fallback defines:
  - `DNS_KEYALG_RSA`
  - `DNS_KEYPROTO_IPSEC`

Research notes:
- This header exposes DNS KEY retrieval and RSA conversion to authentication code when DNSSEC support is compiled in.
