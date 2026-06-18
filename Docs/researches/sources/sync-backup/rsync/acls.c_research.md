# sources/sync-backup/rsync/acls.c

Purpose: converts, transmits, caches, receives, and applies filesystem ACLs for rsync transfers.

Important APIs/types/functions: public `get_acl`, `send_acl`, `receive_acl`, `cache_tmp_acl`, `uncache_tmp_acls`, `set_acl`, `match_acl_ids`, `default_perms_for_dir`, and `free_acl`. Internal structures model rsync ACLs (`rsync_acl`, `ida_entries`, `id_access`) and cached system ACL pairs (`acl_duo`).

Control flow: system ACLs are unpacked into portable rsync ACLs, permission bits are stripped when inferable from mode, ACLs are sent with de-duplicated indexes, received ACLs are cached, IDs are mapped, and destination ACLs are packed/applied. Fake-super stores ACLs in xattrs. Default directory ACLs are read to compute inherited permissions.

State and persistence: global `access_acl_list` and `default_acl_list` cache ACL identities during a run; `prior_*_count` tracks temporary entries for rollback. Persistent effects are real filesystem ACLs or xattr-encoded fake-super ACLs.

Dependencies/integration: depends on `lib/sysacls.h`, uid/gid mapping, xattrs, file-list ACL index macros, protocol varints, mode handling, and daemon/root/read-only flags.

Risks: platform ACL semantics differ greatly; mask/group interactions and special mode bits are sensitive. Stream bounds such as `MAX_WIRE_ACL_COUNT` defend against malformed input.

Test signals: exercised by ACL/xattr test suites and many platform CI jobs with ACL packages installed.
