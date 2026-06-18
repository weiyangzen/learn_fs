# sources/storage-engines/wiredtiger/test/suite/test_cursor_tracker.py

Purpose: reusable cursor test harness, not a standalone test method. It mirrors WiredTiger cursor contents in Python so descendant tests can insert, remove, search, iterate, and verify cursor position and key/value correctness.

Important APIs and types: `TestCursorTracker` extends `WiredTigerTestCase`. It exposes helpers such as `cur_initial_conditions`, `cur_insert`, `cur_remove_here`, `cur_search`, `cur_recno_search`, `cur_first`, `cur_last`, `cur_next`, `cur_previous`, and `cur_check_here`. Encoders map `(major, minor, version)` triples into row-store string keys or column-store recnos.

Control flow: `cur_initial_conditions` populates initial records, closes and reopens the connection to force disk-backed baseline state, then later operations mutate both WiredTiger and Python state (`bitlist`, `vers`, `curpos`, `curbits`, `nopos`, `curremoved`).

State and persistence: Python state distinguishes existing, deleted, positioned, and removed cursor states. Reopening after initial population ensures tests cover both on-disk values and update-list behavior.

Dependencies and risks: uses `wiredtiger`, `wttest`, and `hashlib` for deterministic padding. Since it is a shared harness, mistakes in `bitlist` ordering, recno encoding, or `WT_NOTFOUND` expectations can cascade into many cursor tests.
