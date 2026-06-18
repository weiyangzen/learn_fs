# sources/sync-backup/borg/src/borg/platform/windows_ug.py

Purpose: supplies deterministic placeholder ownership mappings for Windows.

Important APIs/types: cached `_uid2user`, `_user2uid`, `_gid2group`, and `_group2gid`.

Control flow/state: numeric-to-name returns `"root"`; nonempty user/group names map to `0`; empty names return `default`. No OS account lookup is performed.

Dependencies/integration: selected by `platform.__init__` on Win32 and used through public ownership wrappers.

Risks: real Windows security identities are not represented. Values are compatibility placeholders and must not be treated as security evidence.

Test signals: placeholder returns, empty-name defaults, wrapper selection on Windows.
