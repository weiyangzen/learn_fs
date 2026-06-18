# sources/user-network-fs/samba/source3/utils/net_dns.c

Purpose: implements the Kerberos-enabled dynamic DNS update engine used by ADS DNS registration and post-join DNS updates.

Important APIs/types/functions: `DoDNSUpdate()` performs probe/unsigned/signed DNS update transactions; `DoDNSUpdateNegotiateGensec()` negotiates Kerberos/GENSEC signing context; `get_my_ip_address()` discovers usable local interface addresses.

Control flow: `DoDNSUpdate()` validates modes and address inputs, opens a TCP DNS connection, optionally probes, optionally sends unsigned update, and optionally negotiates GSS-TSIG signing and sends signed update. Sufficient flags permit early success. Signed negotiation retries with a Windows 2000 DNS server-type workaround. Interface discovery loads configured interfaces and copies non-loopback, non-link-local addresses.

State and persistence: mutates remote DNS records; no local persistent writes. `get_my_ip_address()` allocates a caller-freed address array.

Dependencies/integration: depends on addns DNS helpers, GENSEC/auth generic client setup, `utils/net_dns.h`, Samba interface helpers, and `cli_credentials`. Called by `net_ads_join_dns.c`.

Risks: flag combinations define security and sequencing; unsigned updates can be sufficient if caller sets that flag. Removal semantics depend on addns update request behavior. Interface discovery can return zero usable addresses despite connectivity.

Test signals: invalid flags; probe-sufficient, unsigned, and signed paths; GENSEC failure and Windows 2000 retry; no-address validation; IPv4/IPv6 interface filtering; DNS response-code failures.
