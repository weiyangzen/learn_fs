<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/patterns_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/patterns_test.py

Purpose: small unit tests for archive item filtering built by `archiver._common.build_filter`.

Important APIs: `PatternMatcher`, `parse_pattern`, `IECommand.Include`, `Item`, and `build_filter`.

Control flow: `test_basic` creates an include matcher for `included` and verifies exact and child paths pass while unrelated paths fail. `test_empty` uses fallback-true matcher to accept anything. `test_strip_components` verifies that filter behavior rejects paths too shallow for `strip_components=1` but accepts deeper paths after stripping.

State and persistence: no persistent state; all state is in matcher instances and synthetic `Item` objects.

Dependencies/integration: integrates pattern parsing with archive filter generation and strip-components logic used by list/extract/recreate flows. Risks are subtle path-depth semantics and fallback handling. Test signals are direct boolean filter results.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/patterns_test.py -->
