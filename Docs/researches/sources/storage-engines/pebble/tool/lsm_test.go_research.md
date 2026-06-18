## sources/storage-engines/pebble/tool/lsm_test.go

Purpose: regression test for `lsmT.buildEdits` when overlapping L0 files are added out of largest-sequence-number order.

Important APIs/types/functions: `TestBuildEditsL0OutOfSeqNumOrder` defines `newL0Table`, creating `manifest.TableMetadata` with overlapping user-key bounds, explicit sequence-number ranges, size, and physical backing. It then constructs two version edits adding high-seq and low-seq L0 tables and calls `l.buildEdits`.

Control flow: the test sets up a default comparer, creates two overlapping L0 tables where the first has larger sequence numbers, builds an `lsmT`, assigns its comparer, and asserts `buildEdits` does not panic and produces two state edits.

State and persistence: all objects are in-memory metadata. No MANIFEST or DB files are used.

Dependencies and integration: uses `manifest.TableMetadata`, `base.InternalKey`, `sstable.Comparers`, `pebble.Options`, and `testify/require`. It specifically verifies that production code uses `manifest.NewVersionWithFiles`, which orders L0 for `L0Organizer`, instead of a testing constructor preserving problematic slice order.

Risks: focused on one panic scenario; it does not validate full JSON output, HTML rendering, edit slicing, or virtual backing behavior.

Test signals: protects against regressions that would reintroduce L0 organizer precondition panics for real manifests where L0 additions are not already sorted by sequence number.
