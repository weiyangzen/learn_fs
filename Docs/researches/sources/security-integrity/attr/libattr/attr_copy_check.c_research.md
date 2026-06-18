## sources/security-integrity/attr/libattr/attr_copy_check.c

Purpose: default xattr copy filter.

`attr_copy_check_permissions` returns true only when `attr_copy_action(name, ctx)` returns zero, preserving backwards-compatible behavior of skipping configured ACL/security metadata unless explicitly allowed elsewhere. State is delegated to `attr_copy_action`'s cached config. Dependencies are public libattr and error context headers. Risks are the name: it returns false for any configured nonzero action, including `permissions`, which may surprise callers. Test signal is default `attr_copy_file` behavior against `xattr.conf`.
