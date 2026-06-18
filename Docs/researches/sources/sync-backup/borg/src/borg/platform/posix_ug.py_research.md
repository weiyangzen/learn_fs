# sources/sync-backup/borg/src/borg/platform/posix_ug.py

Purpose: cached POSIX user/group name and numeric ID lookup helpers.

Important APIs/types: `_uid2user`, `_user2uid`, `_gid2group`, and `_group2gid`, all decorated with `functools.cache`.

Control flow/state: numeric lookups call `pwd.getpwuid` or `grp.getgrgid`; name lookups call `pwd.getpwnam` or `grp.getgrnam`. Missing entries return `default`; empty names return `default` for name-to-ID calls. Cache state is process-local.

Dependencies/integration: selected by `platform.__init__` on POSIX and exposed through public wrappers used by archive metadata handling.

Risks: caches can become stale if account databases change during a process. Missing users/groups are intentionally nonfatal, which helps portability but can mask local changes.

Test signals: successful and missing lookups, empty-name behavior, default propagation, cache clearing under monkeypatches.
