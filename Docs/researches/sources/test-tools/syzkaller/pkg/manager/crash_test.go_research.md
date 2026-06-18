# sources/test-tools/syzkaller/pkg/manager/crash_test.go

Purpose: Exercises `CrashStore` behavior for crash persistence, listing, repro report assembly, memory dump handling, and subsystem extraction from saved reports. It is a manager package test file, so it validates the public behavior of crash storage rather than defining production APIs.

Important APIs and functions: `TestCrashList`, `TestEmptyCrashList`, `TestMaxCrashLogs`, `TestCrashRepro`, `TestCrashMemoryDump`, and `TestGetSubsystems`. These tests instantiate `CrashStore`, call `SaveCrash`, `BugList`, `BugInfo`, `SaveRepro`, `Report`, and the internal `getSubsystems`, and validate `crashHash`-based addressing.

Control flow and state: Tests create temporary workdirs, save synthetic reports under stable titles, and then inspect derived lists or report payloads. `TestMaxCrashLogs` stresses retention by saving 20 crashes while expecting only five crash entries to remain. `TestCrashRepro` verifies that a saved repro enriches the final report with tag, syz repro, C repro, and kernel report. `TestCrashMemoryDump` writes a fake vmcore and expects it copied into crash storage.

Dependencies and integration points: Uses `mgrconfig`, `report.NewReporter`, `repro.Result`, `prog.Prog`, `subsystem.MakeExtractor`, and `osutil.WriteFile`. The four `testdata/*` crash reports feed subsystem extraction, linking this test to report parsing and subsystem path rules.

Risks: The tests depend on filesystem ordering and crash hash layout through public behavior. Subsystem extraction correctness depends on report symbolization/guilty-file heuristics, so fixture drift can cause unrelated failures. Memory dump tests only validate copy/link existence, not cleanup or large dump behavior.

Test signals: Strong regression coverage for `CrashStore` persistence contracts, crash-log retention, repro report formatting inputs, and subsystem mapping for block, HID/USB, mm, and nil cases.
