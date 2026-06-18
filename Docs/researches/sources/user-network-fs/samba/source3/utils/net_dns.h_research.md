# sources/user-network-fs/samba/source3/utils/net_dns.h

Purpose: defines dynamic DNS update flags and declares `DoDNSUpdate()` when Kerberos support is built.

Important APIs/types/functions: flags cover signed, unsigned, and probe modes plus sufficient-success variants. `DoDNSUpdate()` accepts server, domain, hostname, credentials, address list, flags, TTL, and removal mode.

Control flow: none at runtime; `HAVE_KRB5` controls declaration visibility and addns DNS type inclusion.

State and persistence: none directly; the declared function mutates remote DNS records.

Dependencies/integration: includes addns DNS types, forward-declares `struct cli_credentials`, and is consumed by `net_dns.c`, `net_ads_join_dns.c`, and `net_ads.c`.

Risks: low-level flags expose sequencing policy and can be combined incorrectly. The server name parameter is mutable `char *` even though callers treat it as input.

Test signals: compile with/without Kerberos; caller ABI compatibility; flag behavior in DNS update tests.
