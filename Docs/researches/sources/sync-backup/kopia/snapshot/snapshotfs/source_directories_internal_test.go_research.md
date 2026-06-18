# sources/sync-backup/kopia/snapshot/snapshotfs/source_directories_internal_test.go

Purpose: direct tests for safe mount-name generation and collision disambiguation.

Important APIs/types/functions: `TestSafeNameForMount`, `TestDisambiguateSafeNames`, `safeNameForMount`, and `disambiguateSafeNames`.

Control flow: path cases cover Unix roots, trailing slashes, Windows drives, UNC paths, forward slashes, backslashes, and mixed separators. Disambiguation cases feed maps where several originals collapse to the same safe lowercase name and verify deterministic suffixes like `" (2)"`.

State and persistence: pure in-memory string mapping tests.

Dependencies and integration points: protects `AllSourcesEntry` and repository mount browsing from invalid or ambiguous directory names.

Risks and test signals: map iteration is made deterministic by sorting conflicting originals. Recursive disambiguation is tested by including an original that already contains `" (2)"` and collides with a generated suffix.
