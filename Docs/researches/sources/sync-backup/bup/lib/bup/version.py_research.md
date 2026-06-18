## sources/sync-backup/bup/lib/bup/version.py

Purpose: computes Bup’s byte-string version from checkout or archive metadata.

Important APIs and state: imports `checkout_info` when available; otherwise uses `source_info`. Exports `date`, `commit`, `modified`, `base_version`, and `version`. `base_version` is `b'0.34~'`; because it ends in `~`, the commit id is appended. A modified checkout appends `b'+'`.

Integration and risks: Debian-style `~` ordering is intentional. Archive fallback asserts expanded `source_info` values, so packaging must include valid metadata. User-facing commands (`bup version`, installer smoke tests, repair trailers) depend on this. Test signals include `test-install`, `test-help` indirectly, and repair trailer checks in `test-get-repair-bupm` and `test-get-rewrite-missing`.
