# sources/user-network-fs/samba/source4/cldap_server/rootdse.c

Purpose: handles valid CLDAP rootDSE search requests by synchronously querying SAMDB and returning LDAP search entries/results.

Important APIs/functions: `cldapd_rootdse_request()` is the external request entry point. `cldapd_rootdse_fill()` builds and executes the LDB search and converts the result to `ldap_SearchResEntry`.

Control flow: requested attributes are copied into a NULL-terminated array. An LDB base-scope search request is built against `cldapd->samctx` with the incoming LDAP filter tree and timeout. At most one result is accepted. Returned LDB message attributes are moved/stolen into the LDAP response entry unless attributes-only mode suppresses values. The caller sets `remoteAddress` on SAMDB before the synchronous fill and clears it immediately after, then sends a CLDAP reply.

State/dependencies/integration: no database writes. It temporarily stores client address in SAMDB opaque state for audit/logging context. Uses tevent/LDB APIs, SAMDB, LDAP/CLDAP structures, NDR misc, and service task context. Called by `cldapd_request_handler()`.

Risks/test signals: clearing `remoteAddress` is essential with the shared SAMDB context. Attribute value ownership uses talloc stealing from LDB results. Error mapping mixes LDAP and LDB codes. Coverage is expected from DC locator/rootDSE CLDAP integration tests.
