# sources/user-network-fs/samba/source3/passdb/lookup_sid.h

Purpose: public interface and flag definitions for Samba3 SID/name/Unix-ID lookup operations.

Important APIs/types: defines `LOOKUP_NAME_*` flags controlling isolated, remote, group, no-NSS, builtin, well-known, domain-local, local, and all lookup behavior. `struct lsa_dom_info` and `struct lsa_name_info` model `lookup_sids()` results. Declares `lookup_name()`, `lookup_name_smbconf()`, `lookup_name_smbconf_ex()`, `lookup_sids()`, `lookup_sid()`, uid/gid/xid conversion helpers, `sids_to_unixids()`, and `get_primary_group_sid()`.

State and persistence: no state; functions declared here access passdb, winbind, NSS, idmap cache, and secrets through the implementation.

Dependencies and integration: includes generated LSA NDR types and forward declares passwd/unixid structures. Used by smbd/service/auth/passdb code that needs identity translation.

Risks: flag combinations define security-sensitive lookup scope. `LOOKUP_NAME_GROUP` is explicitly documented as a hack for group-preferring smb.conf contexts. Callers must allocate result arrays on a valid talloc context and handle `SID_NAME_UNKNOWN` separately from transport/status failure.

Test signals: compile coverage and behavioral tests for every flag combination exposed to auth/config/RPC callers.
