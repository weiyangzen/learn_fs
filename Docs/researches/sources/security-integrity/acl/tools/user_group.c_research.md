## sources/security-integrity/acl/tools/user_group.c

Purpose: UID/GID display helpers for ACL tools.

`user_name` resolves a UID with `getpwuid` unless numeric output is requested, otherwise formats a decimal string; `group_name` mirrors this with `getgrgid`. State is two static 22-byte buffers used for numeric fallback, so return values are overwritten by later calls and are not thread-safe. Dependencies are libc passwd/group databases and `snprintf`. Risks include static storage reuse and `"?"` fallback if formatting somehow fails. Tests should cover numeric and symbolic modes with missing users/groups.
