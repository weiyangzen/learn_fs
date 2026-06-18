# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnscrypt/dnscrypt.h

Conditional DNSCrypt interface header for Unbound. Contents are compiled only when `USE_DNSCRYPT` is defined.

Important point for this build:
- `dnscrypt_config.h` leaves `USE_DNSCRYPT` disabled, so these declarations are inactive in the OpenBSD `unwind` build.

When enabled, defines:
- DNSCrypt magic/header sizes and padding defaults.
- `KeyPair`, `dnsccert`, `dnsc_env`, and `dnscrypt_query_header`.
- Environment state for certificates, keypairs, provider keys, shared-secret cache, nonce cache, replay counters, and locks.

API when enabled:
- create/apply/delete DNSCrypt environment.
- handle curved and uncurved DNSCrypt requests.
- cache size/compare/delete callbacks for shared secrets and nonce cache.

Role in group:
- Dormant optional interface retained from Unbound.
