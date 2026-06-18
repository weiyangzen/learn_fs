<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtbound.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wtbound.py

Purpose: Common utilities for cursor-bound tests across key/value formats, indexes, column groups, forward/reverse traversal, inclusive/exclusive bounds, and evicted pages.

Important APIs and types: `set_prefix_bound` sets lower/upper string prefix bounds. `bound` and `bounds` model expected bound state and range membership. `bound_base` extends `wttest.WiredTigerTestCase` with table creation, key/value generation, bound setting, and traversal checking methods.

Control flow: `create_session_and_cursor` creates the table, optional column groups or index metadata, populates keys from `start_key` to `end_key`, optionally evicts pages with `debug=(release_evict)`, and returns a cursor. `set_bounds` sets a generated key and calls `cursor.bound`. `cursor_traversal_bound` walks `next` or `prev`, checks `WT_NOTFOUND`, validates every returned key against inclusive/exclusive limits, and compares the observed count to either an explicit count or the computed range.

State and persistence behavior: It persists a table, optional colgroups, and optional indexes in the test home. State flags such as `lower_inclusive`, `upper_inclusive`, `use_index`, and `use_colgroup` define expected traversal semantics. Eviction alters cache residency but not logical data.

Dependencies and integration points: Depends on `wiredtiger`, `wttest.recno`, cursor bound API strings, and tests that provide `uri`, `file_name`, `key_format`, `value_format`, `direction`, and `evict`.

Risks: Expected range math is integer-oriented and must match generated keys for compound/string/raw formats. Prefix-bound string increment only handles simple last-character advancement. Index population temporarily toggles `use_index`, so subclass state misuse can produce wrong expectations.

Test signals: Bound API return codes, traversal counts, ordered key comparisons, and `WT_NOTFOUND` termination provide the main assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtbound.py -->
