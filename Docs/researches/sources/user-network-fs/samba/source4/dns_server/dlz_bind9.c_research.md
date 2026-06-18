# sources/user-network-fs/samba/source4/dns_server/dlz_bind9.c

## Purpose
Implements Samba's BIND9 DLZ driver. It exposes Active Directory DNS zones stored in Samba's `sam.ldb` to BIND, supports lookups and zone transfers, configures writable zones, and handles secure dynamic DNS updates using Kerberos/GENSEC authorization.

## Important APIs, types, and functions
- `struct dlz_bind9_data` is the driver state: parsed options, `samdb`, event/loadparm contexts, transaction token, SOA serial, writable zone list, Kerberos/auth state, cached update session info, and BIND helper callbacks.
- Public DLZ entry points include `dlz_version()`, `dlz_create()`, `dlz_destroy()`, `dlz_findzonedb()`, `dlz_lookup()`, `dlz_allowzonexfr()`, `dlz_allnodes()`, `dlz_newversion()`, `dlz_closeversion()`, `dlz_configure()`, `dlz_ssumatch()`, `dlz_addrdataset()`, `dlz_subrdataset()`, and `dlz_delrdataset()`.
- `b9_format()` converts Samba `dnsp_DnssrvRpcRecord` records into BIND text data.
- `b9_parse()` parses BIND SDLZ record strings back into Samba DNS RPC records.
- `b9_find_zone_dn()` and `b9_find_name_dn()` safely construct LDB DNs for zones/names under known AD DNS containers.
- `b9_set_session_info()` and `b9_reset_session_info()` temporarily switch LDB session info for authorized updates.

## Control flow
`dlz_create()` is the initialization hub. It captures BIND helper callbacks from varargs, disables Samba signal handlers, redirects Samba debug to BIND logging, parses options, initializes loadparm, Kerberos, GENSEC, auth context, locates `dns/sam.ldb`, connects to `samdb`, and stores singleton global state with reference counting.

Lookup paths use `b9_find_zone_dn()` for zone existence and `dlz_lookup_types()` for node lookups. Zone transfer uses `dlz_allowzonexfr()` for allow/deny policy and `dlz_allnodes()` to search all `dnsNode` objects and emit named records. Dynamic update paths require `dlz_newversion()` to start an LDB transaction; BIND then calls add/sub/delete dataset functions; `dlz_closeversion()` commits or cancels.

Secure update authorization runs through `dlz_ssumatch()`: it decodes the GSS key data using DNS keytab credentials, creates session info from the PAC, maps the requested DNS name to an existing node or parent DN, performs a DSDB ACL check for self-write or create-child, then caches the session for the following mutation.

## State and persistence behavior
State is process-global and singleton (`dlz_bind9_state`, refcount), plus mutable per-driver state. Persistent changes are LDB transactions against Samba DNS records. Dynamic update delete operations tombstone individual record values rather than necessarily deleting whole objects. The code caches the current SOA serial from SOA formatting and passes it into `dns_common_replace()` for update-side serial handling.

## Dependencies and integration points
This file bridges BIND's dlopen DLZ ABI (`dlz_minimal.h`) with Samba DSDB, auth/session, GENSEC/Kerberos, dnsserver common helpers, loadparm DNS transfer allow/deny settings, and BIND callback functions such as `putrr`, `putnamedrr`, and `writeable_zone`.

## Risks and edge cases
- Singleton global state and mutable `session_info`/`update_name` are not safe for arbitrary concurrent updates unless BIND's call pattern serializes this driver.
- `dlz_addrdataset()` checks `if (i == UINT16_MAX)` after a `uint16_t` loop, but the intended overflow condition is subtle and depends on `num_recs`.
- `b9_parse()` handles TXT quoting simply and may not fully match all DNS master-file escaping rules.
- Dynamic update correctness depends on `dlz_ssumatch()` being called before mutation; otherwise session info validation fails.
- Zone transfer defaults to deny, which is secure but can surprise deployments without explicit allow lists.
- The driver supports a fixed set of record types; unsupported types fail or are omitted.

## Test signals
No tests are included in this subset. Relevant coverage would include BIND DLZ lookup/allnodes behavior, safe DN construction with hostile names, transfer allow/deny combinations, GSS update authorization, add/modify/delete/tombstone semantics, transaction rollback, duplicate zone handling, and parsing/formatting for every supported record type.
