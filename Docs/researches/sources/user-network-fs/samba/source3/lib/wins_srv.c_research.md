# sources/user-network-fs/samba/source3/lib/wins_srv.c

## Purpose
`wins_srv.c` manages configured WINS server groups, tags, failover selection, and temporary dead-server markers. It supports multiple WINS namespaces by tagging server addresses in `wins server` configuration entries.

## Important APIs and Functions
Public functions are `wins_srv_is_dead`, `wins_srv_alive`, `wins_srv_died`, `wins_srv_count`, `wins_srv_tags`, `wins_srv_tags_free`, `wins_srv_ip_tag`, `wins_server_tag_ips`, and `wins_srv_count_tag`. Internal helpers are `wins_srv_keystr` for gencache keys and `parse_ip` for `tag:ip` entries.

## Control Flow and State
Dead WINS state is stored in `gencache.tdb` under `WINS_SRV_DEAD/<wins_ip>,<src_ip>` for 600 seconds. If Samba itself is a WINS server, many functions return loopback or a single `"*"` tag. Otherwise functions scan `lp_wins_server_list`, parse optional tags, de-duplicate tag lists, choose the first live server for a tag and source IP, or fall back to the first configured server if all are dead.

## Dependencies and Integration Points
It depends on loadparm WINS settings, IPv4 address helpers, `gencache`, and Samba allocation/string wrappers. It integrates with nmbd WINS registration and client WINS lookup logic that need failover across per-interface server groups.

## Risks and Test Signals
This code is IPv4-only (`struct in_addr`, `inet_ntoa`). `inet_ntoa` static buffers are copied quickly in most places, but logging with multiple calls can still be confusing. `wins_srv_tags` can leak partially allocated strings if allocation fails mid-list. Dead state is source-IP-specific, so tests must include multiple source addresses. Test signals include tag parsing, duplicate tag removal, local-WINS mode, all-dead fallback, gencache expiry, and `wins_server_tag_ips` empty/no-match behavior.
