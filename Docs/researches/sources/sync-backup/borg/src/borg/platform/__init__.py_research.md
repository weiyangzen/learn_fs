# sources/sync-backup/borg/src/borg/platform/__init__.py

Purpose: selects platform-specific filesystem APIs and exposes a stable `borg.platform` surface.

Important APIs/types: re-exports xattr, ACL, flag, sync, process, ownership, host identity, and durability helpers. `get_birthtime_ns` normalizes birthtime retrieval. `uid2user`, `gid2group`, `user2uid`, and `group2gid` wrap the selected user/group module for monkeypatchability.

Control flow/state: import-time platform flags choose Linux, FreeBSD, NetBSD, Darwin, generic POSIX, or Windows implementations. Each branch imports concrete functions and sets `platform_ug`. `xattr` is imported explicitly to support packaging.

Dependencies/integration: repositories import `SaveFile`, `SyncFile`, `sync_dir`, and `safe_fadvise` from this package. Archive code uses ownership, ACL, xattr, flags, and process helpers.

Risks: import-time selection is hard to change after import. Missing branch imports break broad filesystem behavior. Birthtime support varies by OS. `platform_ug` must be set in every branch.

Test signals: platform CI branch coverage, birthtime fallback behavior, wrapper monkeypatching, Windows stub behavior, and generic POSIX fallbacks.
