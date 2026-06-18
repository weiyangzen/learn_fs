## sources/security-integrity/attr/include/libattr.h

Purpose: public libattr copy-helper API.

It declares `attr_copy_file`, `attr_copy_fd`, backwards-compatible `attr_copy_check_permissions`, action constants `ATTR_ACTION_SKIP` and `ATTR_ACTION_PERMISSIONS`, and `attr_copy_action`. Control flows into xattr enumeration/copy functions and `/etc/xattr.conf` action lookup. State is caller-provided check callback and error context. Dependencies are `error_context` and installed `EXPORT` handling. Risks include ambiguous callback semantics where zero skips an attribute and default behavior intentionally excludes ACL-related attributes. Tests should cover default action filtering and explicit custom filters.
