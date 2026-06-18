# sources/user-network-fs/samba/source3/libads/ldap.c

## Purpose

`ldap.c` is Samba source3's central ADS LDAP client implementation. It discovers an AD domain controller, opens LDAP/LDAPS/StartTLS sessions, performs SASL or anonymous binds, exposes search helpers, constructs LDAP add/modify/delete operations, and provides higher-level AD object helpers for machine accounts, SPNs, OUs, domain metadata, sites, SIDs, and token groups.

## Important APIs, Types, and Functions

Connection entry points are `ldap_open_with_timeout`, `ads_connect_cldap_only`, `ads_connect_creds`, `ads_connect_simple_anon`, `ads_connect_machine`, `ads_disconnect`, and `ads_zero_ldap`. DC discovery flows through `ads_find_dc`, `resolve_and_ping_dns`, `resolve_and_ping_netbios`, `cldap_ping_list`, `ads_try_connect`, and `ads_fill_cldap_reply`. Search APIs include `ads_do_search`, `ads_do_search_all`, `ads_do_search_all_args`, `ads_do_search_all_sd_flags`, `ads_do_search_all_fn`, `ads_search`, `ads_search_dn`, `ads_msgfree`, `ads_first_entry`, `ads_next_entry`, `ads_first_message`, and `ads_next_message`. Result extraction helpers include `ads_get_dn`, `ads_parent_dn`, `ads_pull_string`, `ads_pull_strings`, `ads_pull_strings_range`, `ads_pull_uint32`, `ads_pull_guid`, `ads_pull_sid`, `ads_pull_sids`, `ads_pull_sd`, and `ads_pull_username`.

Modification helpers use `ADS_MODLIST`, `LDAPMod`, and `berval`: `ads_init_mods`, `ads_mod_str`, `ads_mod_strlist`, `ads_add_strlist`, `ads_gen_mod`, `ads_gen_add`, and `ads_del_dn`. AD object helpers include `ads_find_machine_acct`, `ads_create_machine_acct`, `ads_move_machine_acct`, `ads_leave_realm`, `ads_clear_service_principal_names`, `ads_get_service_principal_names`, `ads_add_service_principal_names`, `ads_find_samaccount`, `ads_get_tokensids`, `ads_domain_sid`, `ads_domain_func_level`, `ads_current_time`, `ads_site_dn`, `ads_site_dn_for_machine`, `ads_upn_suffixes`, `ads_get_joinable_ous`, `ads_config_path`, `ads_get_extended_right_name_by_guid`, `ads_get_sid_from_extended_dn`, `ads_get_upn`, and `ads_check_ou_dn`.

## Control Flow

Connect begins by preserving any previously discovered socket address, resetting LDAP/TLS/wrap state, then resolving either a caller-specified LDAP server or a DC discovered from DNS SRV, site-aware SRV, NetBIOS fallback, or generated krb5 configuration paths. CLDAP/NetLogon replies populate `ads->config` with server name, realm, bind DN, site names, server flags, LDAP port, and socket address. For real LDAP binds, the code opens TCP, optionally sends StartTLS, installs TLS wrapping for LDAPS/StartTLS, stores closest-DC affinity, fetches `currentTime` for time offset, then binds anonymously or via `ads_sasl_bind`.

Searches convert local charset base/filter strings to UTF-8, disable referrals, and call OpenLDAP with Samba timeouts. Paged searches attach no-referrals and paged-results controls, optionally extended-DN or security-descriptor controls, collect cookies, and concatenate pages when OpenLDAP supports `ldap_add_result_entry`. `ads_do_search_all_fn` streams pages through `ads_process_results`, which determines string versus binary handling by asking the callback once per attribute.

Modification paths build talloc-owned `LDAPMod` arrays, UTF-8 encode DNs and string values, normalize list termination, optionally use the permissive modify control, then call OpenLDAP add/modify/delete APIs. Machine-account creation escapes the RDN, encodes quoted unicode password bytes, creates default HOST and RestrictedKrbHost SPNs, and adds a `computer` object. If the machine already exists, it changes `unicodePwd`, toggles `UF_ACCOUNTDISABLE`, and re-reads the object. Realm leave first tries tree-delete control, then falls back to deleting immediate children before deleting the machine object.

## State and Persistence Behavior

Primary runtime state lives in `ADS_STRUCT`: `ads->ldap.ld`, `ads->ldap.ss`, port, last attempt time, TLS wrap data, SASL wrap data, auth flags, KDC server, time offset, page size, realm/workgroup/bind path/server/site fields, and server flags. Discovery writes persistent-ish Samba caches through `sitename_store`, `saf_store`, `namecache_delete`, and negative connection cache helpers. Machine and SPN helpers persist changes in AD itself. Password and TLS/SASL buffers are talloc-owned and freed by `ads_disconnect` or stack frames.

## Dependencies and Integration Points

This file depends on OpenLDAP, Samba CLDAP/NetLogon ping code, tsocket, DNS/namequery DC sorting, gencache-backed sitename storage, passdb credentials, SASL/TLS wrappers, security descriptor and SID parsing, iconv charset helpers, and loadparm settings such as LDAP timeouts and page size. It is integrated by domain join/leave, winbind/idmap queries, `net ads`, printer publishing, schema lookup, SPN tools, and any source3 ADS LDAP consumer.

## Risks and Test Signals

Risks include process-global `SIGALRM` timeout handling, stale or incorrect site/DC caches, negative-cache propagation by IP/name, charset conversion failures, LDAP page-cookie/resource leaks, referral/paged-results interaction, race-prone ranged retrieval when `usnChanged` moves, incorrect RDN escaping, destructive SPN replacement, machine-account password handling, and subtree deletion fallback behavior. Test signals should cover DC discovery with site hit/miss/fallback, CLDAP flag filtering, LDAPS and StartTLS success/failure, SASL sign/seal/strong-auth retry, paged and unpaged searches, extended-DN and SD controls, reconnect after server-down/timeouts, ranged multi-value retrieval with USN restart, machine create/change/move/leave, SPN add/clear, SID/GUID/SD extraction, domain metadata queries, and OU DN validation.
