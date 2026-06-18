# sources/user-network-fs/samba/source3/lib/ldap_escape.c

Purpose: escapes untrusted text for LDAP filters and RDN values.

Important APIs/types/functions: `escape_ldap_string()` and `escape_rdn_val_string_alloc()`.

Control flow: helpers scan input, allocate destination strings, and emit literal or escaped bytes according to LDAP filter/RDN rules.

State/persistence behavior: no global state. Filter results are talloc-owned; RDN results use allocated memory returned to the caller.

Dependencies/integration: used by LDAP query and account-management code.

Risks/test signals: incomplete escaping is LDAP-injection risk; over-escaping breaks valid names. Tests should include control bytes, NUL, `*()\\`, leading/trailing spaces, `#`, commas, plus, and equals.
