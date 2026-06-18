# sources/user-network-fs/samba/source3/lib/lsa.c

Purpose: adds or finds entries in LSA referenced-domain lists for RPC responses involving SIDs.

Important APIs/types/functions: `init_lsa_ref_domain_list()`, generated `struct lsa_RefDomainList`, `struct lsa_DomainInfo`, `dom_sid_equal()`, and `dom_sid_dup()`.

Control flow: scans existing domains for a matching SID when a domain name is provided, otherwise appends at `ref->count`. It enforces `LSA_REF_DOMAIN_LIST_MULTIPLIER`, updates count/max-size, reallocates the domain array, zeroes the new slot, and duplicates the name and SID.

State/persistence behavior: no global state; output is talloc-owned RPC structure data.

Dependencies/integration: depends on generated LSA NDR types and SID/security helpers.

Risks/test signals: wrong counts or allocation ownership can produce malformed RPC replies. Tests should cover zero/multiple domains and NDR encode/decode by callers.
