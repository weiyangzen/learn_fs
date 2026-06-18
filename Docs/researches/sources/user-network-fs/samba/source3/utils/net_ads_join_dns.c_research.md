# sources/user-network-fs/samba/source3/utils/net_ads_join_dns.c

Purpose: provides internal DNS update support for `net ads join` and explicit ADS DNS registration/removal. It resolves nameserver/domain choices, obtains trust credentials after a join, and calls the DNS update engine.

Important APIs/types/functions: `net_update_dns_ext()` is the exported wrapper under `HAVE_KRB5`; `net_update_dns_internal()` discovers nameservers and calls `DoDNSUpdate()`; `net_ads_join_dns_updates()` runs post-join automatic DNS registration.

Control flow: `net_update_dns_ext()` selects hostname or `lp_dns_hostname()`, lowercases it, gathers local non-loopback addresses with `get_my_ip_address()` when needed, and delegates. The internal path derives the DNS domain from the hostname, honors `--dns-ttl`, uses `c->opt_host` as a direct nameserver when present, otherwise looks up NS records and can fall back to rootDSE `rootDomainNamingContext` for forest-root NS records. It iterates nameservers with probe/unsigned/signed flags adjusted for force and removal.

State and persistence: successful calls mutate AD-integrated DNS records. Post-join updates read machine trust credentials with `pdb_get_trust_credentials()` and skip clustered setups and non-AD domains.

Dependencies/integration: depends on libads DNS/LDAP helpers, passdb credentials, `utils/net_dns.h`, `DoDNSUpdate()` from `net_dns.c`, and `libnet_JoinCtx` output from `net_ads_join()`.

Risks: hostnames without a dot cannot produce a DNS domain. Fallback root-domain lookup needs LDAP connectivity. Interface auto-detection may include unwanted non-loopback addresses outside clustered mode. `--force` disables early sufficient success for probe/unsigned phases. Removal intentionally proceeds beyond probe-sufficient success.

Test signals: post-join update on/off; clustered skip; explicit register/unregister; no-domain hostname; TTL behavior; nameserver failover and forest-root fallback; trust-credential failure; forced update.
