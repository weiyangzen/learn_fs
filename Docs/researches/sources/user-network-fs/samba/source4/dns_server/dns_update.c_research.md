# sources/user-network-fs/samba/source4/dns_server/dns_update.c

## Purpose
`dns_update.c` implements RFC2136-style dynamic DNS updates for Samba's AD-backed DNS server. It validates zone/prerequisite/update sections, checks update policy and TSIG authentication, converts DNS wire records into AD `dnsp_DnssrvRpcRecord` values, and writes changes transactionally to `samdb`.

## Important APIs, Types, and Functions
- `dns_server_process_update()` is the public update entry point.
- `check_one_prerequisite()` and `check_prerequisites()` enforce RFC2136 prerequisite semantics, including `ANY`, `NONE`, and exact RRset tests.
- `update_prescan()` rejects out-of-zone and illegal update records before mutation.
- `dns_rr_to_dnsp()` converts `dns_res_rec` records into `dnsp_DnssrvRpcRecord` values for A, AAAA, NS, CNAME, SRV, PTR, MX, and TXT.
- `handle_one_update()` implements add, replace, mass delete, and individual delete behavior.
- `handle_updates()` wraps prerequisite re-check and update application in an LDB transaction and temporarily sets the authenticated TSIG session info.
- `dns_update_allowed()` enforces `allow dns updates` policy and maps authenticated TSIG keys to sessions.

## Control Flow
The entry point requires exactly one question, class `IN` or `ANY`, type `SOA`, and an authoritative zone match with no delegated host part. It exposes the answer section as prerequisites, checks them once, checks update authorization, exposes the authority section as updates, pre-scans them for syntax/zone validity, then calls `handle_updates()`.

`handle_updates()` optionally swaps `DSDB_SESSION_INFO` to the TSIG-authenticated session, converts the zone name to a DN, starts an LDB transaction, re-checks prerequisites inside the transaction, applies each update through `handle_one_update()`, commits on success, cancels on failure, and restores the system session. The double prerequisite check reduces races between preflight and write.

`handle_one_update()` looks up the target node including tombstones, preserves existing tombstone records by starting after them, detects static names, then branches by update class. Zone-class records add/replace data, enforce CNAME exclusivity, and only update SOA when serial increases. `QCLASS_ANY` tombstones matching records or all eligible records, protecting zone-apex SOA/NS. `QCLASS_NONE` tombstones an individual matching record, with special handling for SOA/NS deletion semantics.

## State and Persistence
Updates persist by replacing the AD `dnsRecord` attribute through `dns_replace_records()`. Deletions are represented as `DNS_TYPE_TOMBSTONE` placeholders passed to `dns_common_replace()`, which decides whether to tombstone individual records or the whole node. Dynamic records receive `dwTimeStamp = unix_to_dns_timestamp(time(NULL))` unless the existing name is static.

## Dependencies and Integration Points
The module depends on NDR DNS/DNSP types, `samdb`, `dsdb` utility functions, Samba configuration, auth session state, DNS common lookup/replacement/name matching helpers, and DNS crypto/TKEY state from `dns_server.h`.

## Risks and Edge Cases
- `dns_rr_to_dnsp()` does not implement every DNS type; unsupported update types return `NOT_IMPLEMENTED`.
- SOA serial comparison uses simple `<=` and has a TODO for RFC1982 serial arithmetic.
- Update authorization allows all updates when configuration is `DNS_UPDATE_ON`; secure deployments should use authenticated/secure policy.
- The update path temporarily mutates LDB opaque session info and must always restore it; current cleanup does this after the transaction path.
- A no-op TTL-only replacement may suppress `WERR_ACCESS_DENIED`, intentionally treating denied identical TTL replacement as success.

## Test Signals
Test coverage should exercise RFC2136 prerequisites (`YXDOMAIN`, `NXDOMAIN`, `YXRRSET`, `NXRRSET`), secure vs insecure update policy, TSIG key lookup failures, transactional rollback on a later update failure, CNAME exclusivity, zone-apex SOA/NS deletion protection, tombstoned node resurrection, and unsupported RR types.
