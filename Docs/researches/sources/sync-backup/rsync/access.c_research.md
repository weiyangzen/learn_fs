# sources/sync-backup/rsync/access.c

Purpose: daemon host allow/deny authorization based on hostnames, netgroups, and IP/CIDR address patterns.

Important APIs/types/functions: public `allow_access()`; helpers `match_hostname()`, `match_address()`, `match_binary()`, `make_mask()`, and `access_match()`.

Control flow: `allow_access()` reads module allow/deny lists and forward-DNS policy, then allows explicit allow matches, denies non-matches when only allow is present, rejects deny matches, and allows the rest. `access_match()` tokenizes list entries. Host matching checks reverse DNS/wildcards, optional netgroups, and optional forward DNS of config hostnames. Address matching parses numeric IPv4/IPv6 and masks.

State and persistence: `allow_forward_dns` is a file-static policy cache for the current check; no persistence.

Dependencies/integration: uses daemon config accessors `lp_hosts_allow`, `lp_hosts_deny`, `lp_forward_lookup`, DNS APIs, wildcard matching, logging, and `undetermined_hostname`.

Risks: DNS spoofing/staleness affects decisions; `strtok` and temporary token mutation mean inputs are copied first. IPv6 scope/mask parsing is subtle.

Test signals: covered indirectly by daemon access tests and CI TCP daemon runs.
