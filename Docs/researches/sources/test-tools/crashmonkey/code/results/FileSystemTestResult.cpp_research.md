# sources/test-tools/crashmonkey/code/results/FileSystemTestResult.cpp

Purpose: implements filesystem checker/mount/replay error accumulation and formatting.

Important APIs/functions: constructor and `ResetError()` set `kCheckNotRun`; `SetError()` ORs new error bits into the summary; `GetError()` returns the bitmask; `PrintErrors()` emits every set error; `operator<<` maps bits to text.

Control flow and state: `Tester::test_fsck_and_user_test()` sets mount, fsck, unmountable, snapshot restore, and bio-write errors. `SingleTestInfo` uses the bitmask to classify pass/fixed/required/failed outcomes.

Dependencies: used by `FsSpecific` return mapping, `SingleTestInfo`, and `TestSuiteResult`.

Risks: because `kClean` is bit `1` and `SetError()` ORs, a state can contain both clean and error bits if callers set clean after errors. `PrintErrors()` treats `error_summary_ == 0` as `fsck_not_run`, matching the enum but making "no bits set" distinct from clean. Some result classification checks exact equality and may misclassify combined states.

Test signals: tests should cover combined bits, clean plus error, and exact output strings for every enum.
