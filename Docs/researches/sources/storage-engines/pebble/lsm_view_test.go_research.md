# sources/storage-engines/pebble/lsm_view_test.go

Purpose: this test verifies `DB.LSMViewURL` through a datadriven fixture that defines databases and compares generated visualization URLs.

Important APIs/types/functions: `TestLSMViewURL` uses `datadriven.RunTest` on `testdata/lsm_view`. The `define` command delegates to `runDBDefineCmd` to create a DB from the fixture, then returns `d.LSMViewURL()`.

Control flow: each fixture command opens a DB with default options, closes it after URL generation, and fails on unknown commands or setup errors. The returned URL becomes the datadriven golden output, indirectly validating level construction, key indexing, table details, and URL encoding stability.

State and persistence behavior: DB lifetime is scoped to each command. Test cleanup relies on `defer d.Close()` and `leaktest.AfterTest`. No persistent repo state is modified by the test.

Dependencies and integration points: exercises the DB definition test harness, datadriven framework, leaktest, and the full `LSMViewURL` path including manifest metadata and URL generation.

Risks and test signals: because generated URLs encode structured data, output churn may occur when display formatting or metadata fields change. The test is narrow but useful as a regression signal that the diagnostic URL remains constructible for representative LSMs.
