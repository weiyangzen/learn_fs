# sources/user-network-fs/nfs-utils/support/nfsidmap/umich_ldap.c

Purpose: `umich_ldap.c` implements the `umich_ldap` idmap plugin, mapping NFSv4 names, numeric IDs, and GSS principals through an LDAP schema with configurable object classes and attribute names.

Important APIs and control flow: `umichldap_init` reads `UMICH_SCHEMA` options for server, base DNs, TLS, referrals, SASL, timeout, canonicalization, and attribute mappings. `ldap_init_and_bind` creates a per-request LDAP handle, sets protocol/referral/TLS/SASL options, and binds. `umich_name_to_ids`, `umich_id_to_name`, and `umich_gss_princ_to_grouplist` issue LDAP searches, validate one-result cases, convert `uidNumber`/`gidNumber`, and fill output buffers. Public callbacks are collected in `umichldap_trans`.

State, dependencies, and integration: Global `ldap_info` and `ldap_map` store configuration. The code integrates OpenLDAP, optional Cyrus SASL/GSSAPI, `nfslib` address helpers, and libnfsidmap plugin dispatch.

Risks and test signals: This snapshot contains duplicated tokens around `sasl_interact_cb`, `umich_name_to_ids`, and `umichldap_name_to_uid` that would fail compilation as shown. LDAP filters interpolate unescaped external names/principals, and each lookup opens/binds a new connection. Tests should include build coverage, LDAP fixtures for user/group/principal/group-list mapping, TLS/SASL options, oversized filters, malicious filter characters, and group-list size negotiation.
