# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ProgressBarTest.cpp

Purpose: Tests progress bar output behavior, including rendering at start, intermediate progress, completion, and likely edge values.

Important APIs and types: Uses `cpp-utils/io/ProgressBar` with GoogleTest and captured output expectations.

Control flow: Tests construct a progress bar, update progress amounts, and compare emitted console/output strings or lack of crashes depending on scenario.

State and persistence behavior: State is in-memory progress counters and captured output. No persistent state.

Dependencies and integration points: Progress bar output is user-facing in CLI flows; this test guards formatting and update behavior.

Risks: Progress formatting can be terminal-width or carriage-return sensitive. Tests may be brittle if presentation changes intentionally.

Test signals: Expected output for progress states and successful handling of boundary progress values.
