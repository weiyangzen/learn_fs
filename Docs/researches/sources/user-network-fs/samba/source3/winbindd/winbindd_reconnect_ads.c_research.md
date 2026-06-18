<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect_ads.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect_ads.c

## Purpose
This file wraps the ADS winbind backend with a narrow retry layer. It exposes `reconnect_ads_methods`, a `struct winbindd_methods` table whose entries call the matching `ads_methods` implementation and then retry once when the returned status looks like a transient LDAP/RPC transport problem. It exists only under `HAVE_ADS`, so non-ADS builds omit it.

## Important APIs, Types, And Functions
The central helper is `ldap_reconnect_need_retry()`, which refuses retries for successful statuses, informational/non-error statuses, expected lookup misses such as `NONE_MAPPED`, `NO_SUCH_USER`, `NO_SUCH_GROUP`, `NO_SUCH_ALIAS`, `NO_SUCH_MEMBER`, `NO_SUCH_DOMAIN`, `NO_SUCH_PRIVILEGE`, and `NO_MEMORY`, and returns true for other errors. The wrapper functions mirror the winbind backend vtable: `query_user_list`, `enum_dom_groups`, `enum_local_groups`, `name_to_sid`, `sid_to_name`, `rids_to_names`, `lookup_usergroups`, `lookup_useraliases`, `lookup_groupmem`, `lookup_aliasmem`, `lockout_policy`, `password_policy`, and `trusted_domains`.

## Control Flow
Every method calls the corresponding `ads_methods.*` function first. If the status matches the retry predicate, the same method is invoked a second time with the same arguments and its result is returned. Some name and policy paths use the generic `reconnect_need_retry()` instead of the LDAP-specific predicate, while list and membership LDAP-heavy paths use `ldap_reconnect_need_retry()`.

## State And Persistence Behavior
The file keeps no private persistent state. It relies on ADS connection state owned by the wrapped backend and on retry side effects in lower layers. Output pointers are those supplied by callers and may be overwritten by either the first successful call or the second retry.

## Dependencies And Integration Points
It depends on `winbindd.h`, `ads_methods` from `winbindd_ads.c`, the generic reconnect predicate from the non-ADS reconnect layer, NTSTATUS helpers, and the `winbindd_methods` backend dispatch contract. Integration is through domain backend selection for ADS domains that need reconnect behavior without duplicating ADS lookup code.

## Risks And Test Signals
The retry policy must not retry semantic "not found" answers, otherwise callers can experience duplicate LDAP traffic and misleading logs. Since retries reuse the same output pointers, callees must tolerate partial output from a failed first attempt or clean it internally. Good signals are ADS lookup tests with dropped LDAP connections, expected miss cases that return immediately, and build coverage with and without `HAVE_ADS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect_ads.c -->
