# sources/user-network-fs/samba/source4/libcli/ldap/ldap_ildap.c

Purpose: synchronous convenience API similar to traditional LDAP search calls, built on the async LDAP request layer.

Important APIs: `ildap_count_entries()`, `ildap_search_bytree()`, and `ildap_search()`.

Control flow: `ildap_search()` parses a string filter into an LDB parse tree then delegates to `ildap_search_bytree()`. The by-tree function constructs a SearchRequest message, counts requested attributes, attaches controls, sends it, then iterates `ldap_result_n()` until `SearchResultDone` or error. Entry and reference messages are accumulated into a null-terminated result array; response controls can be stolen to caller output.

State and persistence: results and response controls are talloc-owned by the connection/caller memory. No persistent storage.

Dependencies and integration: depends on `ldap_client.h`, LDAP message structs, LDB parse trees, and request/result functions. It is a blocking wrapper over the event loop.

Risks: `*results` is unconditionally dereferenced, so caller must provide a valid output pointer. The function reparents `req` under `msg` in an unusual direction and does not visibly free `msg` on all success paths, so ownership assumptions rely on request lifetime. Test signals include empty result sets, search references, response controls, invalid filter expressions, no-more-entries normalization, and attribute-only searches.
