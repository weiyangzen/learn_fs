# sources/user-network-fs/samba/source3/libads/ldap_utils.c

## Purpose

`ldap_utils.c` provides resilient ADS LDAP search wrappers: reconnect-on-error, page-size backoff on timeouts, SID/DN convenience searches, security-descriptor and extended-DN controls, and ranged multi-value retrieval.

## Important APIs, Types, and Functions

`ads_set_reconnect_fn` installs a callback for obtaining credentials during reconnect. Search APIs are `ads_do_search_retry`, `ads_search_retry`, `ads_search_retry_dn`, `ads_search_retry_dn_sd_flags`, `ads_search_retry_extended_dn_ranged`, `ads_search_retry_sid`, and `ads_ranged_search`. Internal helpers are `adjust_ldap_page_size`, `ads_do_search_retry_internal`, `ads_do_search_retry_args`, and `ads_ranged_search_internal`.

## Control Flow

`ads_do_search_retry_internal` first avoids immediate reconnect churn if the LDAP handle is absent and the last attempt is recent. It performs anonymous unpaged search for anonymous binds and paged search for authenticated binds. On failure, it optionally halves LDAP page size for meaningful IO timeouts, frees partial results, disconnects, asks the registered reconnect callback for credentials, reconnects with `ads_connect_creds`, and retries up to three attempts.

Ranged search builds an attribute list containing the ranged attribute and `usnChanged`, then loops while AD reports more values. It records the first `usnChanged`, appends returned range chunks via `ads_pull_strings_range`, and restarts up to five times if `usnChanged` changes between range reads.

## State and Persistence Behavior

State is stored in `ads->auth.reconnect_state`, `ads->ldap.ld`, `ads->ldap.last_attempt`, and `ads->config.ldap_page_size`. Ranged-search accumulated strings are talloc-owned by the caller. No durable state is written, but reconnect mutates the live ADS connection.

## Dependencies and Integration Points

It depends on `ldap.c` search/connect/result helpers, `cli_credentials`, loadparm LDAP page-size settings, SID hex encoding, security descriptor control OIDs, and extended-DN control OIDs. It is the safer search layer for callers that need long-running winbind/domain queries to survive dropped LDAP connections.

## Risks and Test Signals

Risks include retrying non-transient LDAP errors, losing the original error after reconnect failure, page-size reduction affecting later callers on the same `ADS_STRUCT`, range retrieval aborting on concurrent object modifications, and a bug-like assignment to local `strings = NULL` instead of `*strings = NULL` on ranged-search failure. Tests should simulate server-down, timeout, reconnect callback failure, strong success after reconnect, anonymous versus authenticated search paths, SD/extended-DN controls, SID special DN searches, ranged values with final `*`, malformed range names, and USN restart exhaustion.
