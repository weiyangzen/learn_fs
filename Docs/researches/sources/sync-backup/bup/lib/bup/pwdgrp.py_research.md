<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/pwdgrp.py -->
# sources/sync-backup/bup/lib/bup/pwdgrp.py

## Purpose
This module wraps password and group database lookups so bup can work consistently with bytes rather than locale-decoded strings, and caches lookups for metadata capture/restore.

## Important APIs, Types, And Functions
Core types are `Passwd` and `Group`. Lookup APIs are `getpwuid()`, `getpwnam()`, `getgrgid()`, `getgrnam()`, `pwd_from_uid()`, `pwd_from_name()`, `grp_from_gid()`, `grp_from_name()`, `username()`, and `userfullname()`.

## Control Flow
Raw `_helpers` lookups return tuples, which are wrapped into slot-based bytes objects. Cache helpers use `helpers.cache_key_value()` to memoize both hits and misses, and successful lookups populate reverse caches. `username()` and `userfullname()` lazily derive current-user names from uid and GECOS fields.

## State And Persistence Behavior
Persistent state is none. In-memory state includes uid/name and gid/name caches plus current-user cached values.

## Dependencies And Integration Points
It depends on `_helpers` platform lookup functions and `helpers.cache_key_value()`. `metadata.py` uses it to record user/group names and to map restored names back to ids.

## Risks And Edge Cases
Lookups can return `None`; callers must handle missing users/groups. `username()` assumes `pwd_from_uid(uid)` is not `None` before accessing `.pw_name`, so unusual systems without a passwd entry for the current uid could fail. Group password may be `None` on Android and is explicitly tolerated.

## Test Signals
Metadata tests, owner mapping restore tests, and platform integration tests cover most behavior indirectly. Focused tests should verify cache hit/miss behavior, byte enforcement, absent users/groups, and fallback current-user strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/pwdgrp.py -->
