## sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/main_test.go

This test file covers pure helper logic in `fuzz-action`. `TestReadSectionHashes` verifies JSON decoding into `build.SectionHashes`. `TestShouldSkipFuzzing` validates empty-symbol behavior, exact equality, ignored volatile Linux data symbols, different hashes, and different symbol counts. `TestBugTitleRe` verifies default empty regexp matches all titles and prefix regexp filtering.

The tests do not execute diff fuzzing, corpus download/merge, artifact compression, or API reporting. They are nevertheless important guards for the skip optimization that determines whether fuzzing is run at all.
