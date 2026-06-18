# Research: sources/storage-engines/pebble/record/rotation_test.go

- **Purpose:** Datadriven coverage for `RotationHelper` state transitions and rotation decisions.
- **Important APIs/types/functions:** `TestRotation` constructs one `RotationHelper`, parses integer command arguments, and supports commands `add`, `should-rotate`, and `rotate`. For mutating commands, it returns `DebugInfo`; for decision commands, it returns the boolean result.
- **Control flow:** The test runs `datadriven.RunTest` over `testdata/rotation`. Each command mutates or queries the same helper instance, making the test file a readable scenario log for cumulative record/snapshot behavior.
- **State and persistence behavior:** No persistence. The test observes in-memory `lastSnapshotSize` and `sizeSinceLastSnapshot` after each command.
- **Dependencies:** Depends on `datadriven`, `fmt`, `strconv`, and `testing`.
- **Integration points:** Provides the main regression signal for log-rotation policy used by higher-level record-log consumers.
- **Risks:** The test is scenario-based and only covers cases present in `testdata/rotation`; it will not prove all arithmetic boundary conditions unless the datadriven file includes them. It shares one helper across commands, so unexpected command ordering in testdata would change later expectations.
- **Test signals:** Failures show up as mismatched boolean rotation decisions or debug state strings, usually indicating a policy threshold or reset behavior change.
