## sources/security-integrity/acl/tools/user_group.h

Purpose: declares ACL tool user/group name formatting helpers.

The header includes `sys/types.h`, `pwd.h`, and `grp.h`, and exposes `user_name(uid_t,int)` and `group_name(gid_t,int)`. It is consumed by display-oriented ACL tools such as `getfacl`. There is no persistent state in the header, but callers must treat returned pointers as borrowed static or libc-owned storage. Risks are missing include guards and the typo-like parameter name `gid_t uid` for `group_name`. Tests are through ACL output formatting with `--numeric`.
