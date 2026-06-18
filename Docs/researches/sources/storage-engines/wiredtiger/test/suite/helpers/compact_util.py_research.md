# sources/storage-engines/wiredtiger/test/suite/helpers/compact_util.py

Purpose: shared base class for background and file compaction Python tests.

Important APIs and control flow: methods delete ranges, populate tables, truncate bounded cursor ranges, read compaction-related connection/data-source statistics, compute file sizes through statistics, count compacted files, and turn background compaction on/off while polling `background_compact_running`.

State and persistence behavior: mutates test tables through inserts/removes/truncate and mutates connection background compaction state via `session.compact(None, 'background=...')`. Reads statistics through short-lived cursors.

Dependencies and integration points: extends `wttest.WiredTigerTestCase`, imports `wiredtiger.stat`, and expects tests to create compatible URIs/key formats. It integrates with WiredTiger background compaction statistics.

Risks: polling loops lack explicit timeout in `turn_on_bg_compact`/`turn_off_bg_compact`, so a stuck state can hang until the outer test timeout. `populate()` loops `range(start_key, num_keys)`, treating `num_keys` as an exclusive stop rather than a count.

Test signals: stats such as bytes recovered, pages rewritten, files skipped, and background running/success counters drive assertions in compaction tests.
