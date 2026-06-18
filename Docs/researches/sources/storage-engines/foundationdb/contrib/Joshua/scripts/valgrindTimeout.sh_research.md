# sources/storage-engines/foundationdb/contrib/Joshua/scripts/valgrindTimeout.sh

Purpose: timeout companion for Valgrind jobs. It runs `test_harness.timeout --use-valgrind` so timeout summaries also parse available Valgrind XML files.

Important APIs and control flow: no direct options except the hard-coded Python flag. The timeout module recursively locates trace directories and `valgrind*.xml`.

State and persistence: reads current-directory artifacts and writes summaries to stdout.

Dependencies and integration: depends on TestHarness2 timeout and valgrind parser modules.

Risks and test signals: multiple Valgrind XML files are combined with each trace run, which can over-report if stale XML remains. Test with one trace run and one Valgrind XML to verify `ExternalTimeout` plus `ValgrindError` handling.
