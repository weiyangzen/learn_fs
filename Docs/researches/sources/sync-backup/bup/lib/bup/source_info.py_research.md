## sources/sync-backup/bup/lib/bup/source_info.py

Purpose: archive-time fallback metadata for source checkout identity. It is intended for Git archive keyword expansion.

Important APIs and state: exports `commit`, `date`, and `modified`. In the source tree these default to `$Format:%H$`, `$Format:%ci$`, and `False`; archive generation can expand the placeholders. `version.py` imports this when `checkout_info` is unavailable.

Integration and risks: correctness depends on release/archive tooling replacing the placeholders. `version.py` asserts that fallback archive values no longer start with `$Format`, so an unexpanded archive without `checkout_info` fails fast. Test signals are indirect through `bup version`, `test-install`, and release/versioning tests outside this subset.
