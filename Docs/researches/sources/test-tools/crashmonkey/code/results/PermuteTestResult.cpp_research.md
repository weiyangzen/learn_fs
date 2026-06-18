# sources/test-tools/crashmonkey/code/results/PermuteTestResult.cpp

Purpose: implements formatting for the crash state selected by a permuter.

Important APIs/functions: `PrintCrashStateSize()` prints the count of bios/sectors; `PrintCrashState()` prints `(bio_index)` or `(bio_index, sector_index)` tuples depending on whether entries are full bios.

Control flow and state: `RandomPermuter` fills `crash_state`; `SingleTestInfo::PrintResults()` calls these methods for every test.

Dependencies: relies on `DiskWriteData` fields `bio_index`, `bio_sector_index`, and `full_bio`.

Risks: terminology "bios/sectors" is intentionally ambiguous for mixed modes. Empty state prints a size but no tuple list. Output is human-readable rather than machine-parseable.

Test signals: verify formatting for empty, full-bio, sector-only, and mixed crash states.
