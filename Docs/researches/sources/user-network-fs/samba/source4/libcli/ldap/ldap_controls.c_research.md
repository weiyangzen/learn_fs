# sources/user-network-fs/samba/source4/libcli/ldap/ldap_controls.c

Purpose: maps known LDAP/LDB control OIDs to ASN.1 encode/decode helpers for Samba's LDAP client/server message codecs.

Important APIs: `samba_ldap_control_handlers()` returns the static `ldap_known_controls` table. Internal functions encode/decode paged results, SD flags, search options, extended DN, server sort request/response, ASQ, DirSync/DirSyncEx, VLV request/response, OpenLDAP dereference, verify-name, policy hints, and zero-length flag controls.

Control flow: each decoder loads a control `DATA_BLOB` into `asn1_data`, validates expected sequence/context tags, allocates the corresponding LDB/DSDB control structure, copies strings or binary cookies into talloc memory, and returns a typed pointer. Encoders mirror the structure into ASN.1 and extract a blob. The table associates network-capable controls with handlers and marks internal-only controls with null encode/decode handlers.

State and persistence: no global mutable state; only a static const handler table. All decoded objects live under caller-provided memory.

Dependencies and integration: depends on LDB controls, Samba ASN.1 utilities, DSDB/SAMDB control definitions, UTF-16 conversion, and LDAP attribute decoding for OpenLDAP dereference results. It is called by LDAP message encode/decode in `ldap_client.c`.

Risks: many decode failure paths return false without freeing partially allocated ASN.1 contexts, acceptable under talloc parent lifetimes but worth leak-testing. Incorrect tag handling can reject valid server controls or accept malformed ones. UTF-16 length conversion in verify-name must handle malformed data. Test signals include round-trip encode/decode for each supported control, empty extended-DN and flag controls, critical unknown/undecoded control behavior via `ldap_client.c`, cookies with zero and nonzero length, VLV offset/assertion variants, and OpenLDAP dereference attributes.
