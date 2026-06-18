# sources/user-network-fs/samba/source3/passdb/lookup_sid.c

Purpose: canonical Samba3 name/SID/Unix-ID translation layer. It resolves names to SIDs, SIDs to names, SIDs to uid/gid/unixid, uid/gid to SIDs, and primary group SIDs, combining local SAM, BUILTIN/well-known domains, Unix users/groups, passdb, idmap cache, winbind, trusted domains, and fallback Unix SID domains.

Important APIs and flow: `lookup_name_internal()` parses `DOMAIN\name`, UPN, or isolated names, then follows Windows-like lookup order controlled by `LOOKUP_NAME_*` flags. `lookup_name_smbconf_ex()` qualifies smb.conf names against default domain, own SAM, then Unix Users/Groups. `lookup_sids()` groups requested SIDs by domain, handles domain SIDs specially, applies LSA lookup levels, bulk-resolves RIDs with `lookup_rids()`, and returns `lsa_dom_info`/`lsa_name_info`. `lookup_sid()` is a single-SID wrapper. `xid_to_sid()`, `uid_to_sid()`, `gid_to_sid()`, `sids_to_unixids()`, `sid_to_uid()`, and `sid_to_gid()` use direct Unix SID checks, idmap cache, winbind, passdb legacy mapping, and fallback `S-1-22` Unix SIDs. `get_primary_group_sid()` maps a user's primary gid and forces Domain Users if no valid domain group can be proven.

State and persistence: no owned durable state, but it reads secrets for domain SIDs/trusts, passdb mappings, NSS passwd/group, idmap cache, winbind caches, and local/global SID constants. Some paths call `become_root()` for passdb access.

Dependencies and integration: passdb, secrets, idmap cache, winbind client utilities, libwbclient, bitmap tracking, SID utility libraries, loadparm settings (`lp_workgroup()`, separator/default domain), and domain role macros.

Risks: lookup order is compatibility-sensitive and flag-dependent; changing it can alter access-control semantics. Remote winbind status errors sometimes propagate early. Bulk SID mapping uses fixed `LSA_REF_DOMAIN_LIST_MULTIPLIER`, so too many domains fail. `sids_to_unixids()` allocates a bitmap but does not explicitly free it; it is parented under `wbc_sids`, so freeing that parent is relied upon. Primary group fallback deliberately masks mapping failure with Domain Users for operability.

Test signals: RPC-LSALOOKUP level matrix, qualified/unqualified smb.conf names, BUILTIN/well-known/domain SID cases, Unix Users/Groups direct mappings, winbind failure/unknown paths, idmap negative cache fallback, trusted domain lookup, primary group validation, and mixed-domain bulk lookup.
