## sources/storage-engines/pebble/sstable/block/flush_governor_internal_test.go

Purpose: Unit-tests the unexported allocation class selection helper used by `FlushGovernor`.

Important APIs/types/functions: `TestFindClosestClass` calls `findClosestClass` against fixed size classes `[10,20,30,50]`.

Control flow: The test enumerates targets below, exactly at, between, and above classes, checking that the closest class is selected, with ties resolved by the existing comparison rule.

State and persistence behavior: No persistent state. It protects a decision that affects physical block boundaries.

Dependencies and integration points: Standard `testing` only; same package access permits testing the unexported helper.

Risks: Does not test unsorted classes or empty slices; those are caller assumptions.

Test signals: Focused signal for boundary math around closest-class choice.
