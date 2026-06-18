<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/set_test.go -->
# sources/storage-engines/pebble/internal/problemspans/set_test.go

Purpose: validates `Set` with datadriven scenarios and randomized comparison to a naive implementation.

Important APIs/types: `TestSet`, `parseSetLine`, `TestSetRandomized`, `naiveSpan`, and `naiveSet` with `Add`, `Overlaps`, and `Excise`.

Control flow and state: datadriven tests maintain mocked monotonic time and support `reset`, `add`, `excise`, `overlap`, and `is-empty`, printing the active set after each command. Randomized tests run 1000 trials of 300 operations over random key bounds, adding expiring spans, excising exclusive bounds, querying overlaps, and advancing time; every query is checked against the naive span list.

Dependencies and integration: uses `base.UserKeyBounds`, `crtime.Mono`, datadriven, and random package. The randomized test is a strong signal for endpoint and expiration semantics. Gaps include concurrent use, inclusive excise in the naive model, and very large span counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/set_test.go -->
