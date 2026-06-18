# sources/object-store/apache-ozone/hadoop-ozone/freon/src/test/java/org/apache/hadoop/ozone/freon/TestProgressBar.java

## Purpose
`TestProgressBar` verifies that Freon's `ProgressBar` emits output while tracking a changing counter through its start/shutdown lifecycle.

## Important APIs, Types, and Functions
The test uses JUnit 5 with `MockitoExtension`, a mocked `PrintStream`, an `AtomicLong` counter, and a `LongSupplier`. `setupMock()` initializes the counter and mock. `testWithRunnable()` creates a progress bar with max value 10 and a label supplier, starts it, increments the counter, shuts it down, and verifies the stream printed characters and strings.

## Control Flow
The test starts the progress bar thread before running a local counter-incrementing task. Shutdown is called after the task, and Mockito verifies that output occurred at least once.

## State and Persistence Behavior
All state is in memory. The test observes side effects on a mocked stream only.

## Dependencies and Integration Points
It covers `ProgressBar`, which is used by Freon generators such as `RandomKeyGenerator` to present progress during long-running operations and cleanup.

## Risks and Edge Cases
The test proves emission, not precise rendering, terminal behavior, or timing. Because the progress bar is asynchronous, the test intentionally uses broad `atLeastOnce()` verification.

## Test Signals
Provides a smoke test for progress bar lifecycle and stream interaction. It does not validate termination on error, complete output format, or long-duration behavior.
