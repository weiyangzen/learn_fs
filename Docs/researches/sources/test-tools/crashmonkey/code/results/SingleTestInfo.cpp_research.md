# sources/test-tools/crashmonkey/code/results/SingleTestInfo.cpp

Purpose: implements per-crash-state result classification and detailed log printing.

Important APIs/functions: constructor resets embedded fs/data results. `GetTestResult()` classifies a test as passed, fsck fixed, fsck required, or failed based on exact fs/data states. `PrintResults()` writes test number, result, data/fsck error details, crash-state tuple list, last checkpoint, and raw fsck output. `operator<<` prints result labels.

Control flow and state: `Tester` creates one `SingleTestInfo` per random or checkpoint replay, fills `test_num`, `permute_data`, `fs_test`, and `data_test`, prints it, and tallies it in `TestSuiteResult`.

Dependencies: depends on `DataTestResult`, `FileSystemTestResult`, and `PermuteTestResult`.

Risks: exact equality against fsck bitmasks can misclassify combined states. `PrintResults()` prints data errors before fs errors, so fs-only failures may show a blank data-error field. If fsck returned `kCheck`, it prints `fs_test.error_description`; otherwise it prints data description, which can hide filesystem context for other fs errors.

Test signals: classification matrix tests are important for combinations of clean, fixed, kernel mount, unmountable, bio-write, and data errors.
