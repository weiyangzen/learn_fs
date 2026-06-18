# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dnssec.c

This file implements optional DNSSEC KEY record retrieval for IKE authentication keys.

Key responsibilities:
- Builds DNS names from peer ID payloads.
- Fetches DNS KEY records through `getrrsetbyname`.
- Requires validated DNSSEC responses.
- Filters KEY records for IPsec protocol and requested algorithm.
- Converts DNS RSA KEY wire format into an OpenSSL RSA object.

Important functions:
- `dns_get_key(int type, struct message *msg, int *keylen)`: retrieves a matching DNS KEY record for RSA signature authentication.
- `dns_RSA_dns_to_x509(u_int8_t *key, int keylen, RSA **rsa_key)`: parses DNS RSA exponent/modulus format into `RSA`.

Notable behavior:
- Supports RSA signature lookup; RSA encryption and DSS paths are stubbed out.
- IPv4 IDs are converted to reverse `in-addr.arpa` names.
- FQDN IDs get a trailing dot.
- USER_FQDN IDs are converted from `user@host` to `user._ipsec.host.` by default.
- IPv6 ID DNS lookup is not implemented.
- Unvalidated DNS responses are rejected.
- Only the first matching usable key is returned.

Dependencies:
- Optional LWRES headers when built with `LWRES`; otherwise standard resolver headers.
- Exchange/message ID data.
- IPsec/IKE numeric constants.
- OpenSSL RSA and BIGNUM APIs.

Research notes:
- The file is not in the default Makefile source list unless DNSSEC support is enabled.
- It mutates the USER_FQDN ID buffer temporarily by inserting a NUL at `@`, which callers must account for if sharing that storage.
