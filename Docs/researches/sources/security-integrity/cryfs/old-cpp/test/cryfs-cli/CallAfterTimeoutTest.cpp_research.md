# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CallAfterTimeoutTest.cpp

Purpose: Tests `CallAfterTimeout`, a timer helper that invokes a callback after a delay unless reset. It verifies one-shot behavior and reset behavior.

Important APIs and types: Uses `cryfs-cli/CallAfterTimeout.h`, `unique_ref`, atomics, and GoogleTest. Fixture helper `callAfterTimeout` likely constructs the timer with a test callback and timeout.

Control flow: Tests start a timer, optionally reset it once or twice, wait enough time, and assert callback count/state. `DoesntCallTwice` ensures callbacks are not repeated after firing.

State and persistence behavior: State is in-memory timer/thread state and atomic callback counters. No persistence.

Dependencies and integration points: Supports CLI auto-unmount or idle-timeout behavior.

Risks: Timing tests can be flaky under scheduler delays. Reset races are the key correctness concern.

Test signals: Callback fires after no reset, fires only once, and delayed firing follows one or two resets.
