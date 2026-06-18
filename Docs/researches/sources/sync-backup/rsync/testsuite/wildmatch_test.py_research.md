# sources/sync-backup/rsync/testsuite/wildmatch_test.py

Purpose: wrapper around the `wildtest` C helper to exercise rsync’s `wildmatch()` and `wildmatch_array()`/join behavior over the canonical `wildtest.txt` cases.

Important APIs and flow: iterates over twelve option sets, including plain matching plus combinations of `-x` explode sizes and `-e` empty-string insertion controls. For each, it runs `TOOLDIR/wildtest` with the option set and `SRCDIR/wildtest.txt`. Return code must be zero and stdout must exactly equal `No wildmatch errors found.\n`.

State and persistence: no mutable filesystem state. It depends on build output and the source test data file.

Dependencies and integration: connects to `wildtest.c` and `lib/wildmatch.c`, including array-fragment matching used by rsync filters. Risks are exact stdout coupling and helper availability. Test signal is strong because the helper validates every line and reports internal mismatch counts.
