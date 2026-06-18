<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor18.py

Purpose: exhaustive version-cursor test for full updates, tombstones, history-store records, prepared updates, visibility filtering, cross-key iteration, and start-timestamp filtering.

Important APIs and control flow: row and variable column scenarios run with default and `cross_key=true` version cursor config. Helpers create a file, open `debug=(dump_version=(...))` cursors, and verify timestamp/type/prepare/flags/location/value fields. Tests cover in-memory update chains, on-disk pages after `debug=(release_evict)`, deletion combinations, history-store placement, multiple keys, cursor reuse, prepared full values and tombstones, visible-only skipping of invisible/prepared records, unpositioned iteration, concurrent inserts during traversal, and inclusive/exclusive start timestamp behavior.

State, persistence, and dependencies: state spans update chains, disk images, history store, timestamps, prepared transactions, tombstones, and version cursor internal scan state. Dependencies are `wiredtiger`, `wttest`, statically known value-field layout, and WT timestamp helpers.

Integration points: targets debug dump-version cursor semantics and history-store visibility across access methods.

Risks and test signals: expected numeric fields are tightly coupled to internal version-cursor encoding. Pass signals are exact field tuples, correct `WT_NOTFOUND`, and enforced cross-key/positioning rules.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor18.py -->
