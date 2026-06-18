<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/simplify_test.go -->
## sources/storage-engines/pebble/metamorphic/simplify_test.go

Purpose: datadriven tests for key simplification of metamorphic operation streams.

Important APIs and functions: `TestSimplifyKeys` runs `simplify-keys` commands from `testdata/simplify`. It passes `TestkeysKeyFormat` and toggles suffix-preserving behavior when the datadriven command has a `retain-suffixes` argument.

Control flow: each datadriven command invokes `TryToSimplifyKeys`, converts the resulting bytes to string, and returns them for golden comparison. Unknown commands produce a diagnostic string.

State and persistence: no persistent state. The test validates pure parse/rewrite/format behavior over fixture inputs.

Dependencies and integration: integrates `TryToSimplifyKeys`, parser formatted-key hooks, `TestkeysKeyFormat`, operation key rewriting, and datadriven expected output files.

Risks and gaps: the test exercises fixture cases, not exhaustive generated operation streams. It does not explicitly assert the nil-return path for more than 26 distinct keys unless covered in fixture data.

Test signals: golden output captures ordering, suffix retention, and formatting stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/simplify_test.go -->
