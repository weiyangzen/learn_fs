# File Research: sources/virtualization/libguestfs/daemon/acl.c

Implements ACL optional-group support when libacl is available.

Key points:
- `optgroup_acl_available` reports support under `HAVE_ACL`.
- `do_acl_get_file` accepts `access` or `default`, calls `acl_get_file` inside the sysroot chroot, converts ACLs to text, duplicates libacl-owned strings, and returns caller-owned memory.
- `do_acl_set_file` parses ACL text with `acl_from_text` and applies it inside the sysroot.
- `do_acl_delete_def_file` removes a directory’s default ACL inside the sysroot.
- Without libacl, `OPTGROUP_ACL_NOT_AVAILABLE` supplies unavailable stubs.
