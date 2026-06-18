<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/deck_test.go -->
# sources/storage-engines/pebble/internal/randvar/deck_test.go

Purpose: smoke test for `Deck`.

Important APIs/functions: `TestDeck` creates `NewDeck(nil, 10, 20, 20, 0, 30)`, draws 10,000 samples, and optionally prints a histogram through `dumpSamples` when verbose.

Control flow and state: the test exercises repeated deck reshuffling and confirms only that no panic occurs under a normal non-empty weight set.

Dependencies and integration: reuses `dumpSamples` from `skewed_latest_test.go`. Risk coverage is shallow: it does not assert frequencies, zero-weight exclusion, empty deck behavior, or concurrency. It is primarily a manual visualization aid under verbose test runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/deck_test.go -->
