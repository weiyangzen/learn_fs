# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/assert_debug_test.cpp

Purpose: Tests the debug-build behavior of CryFS assertion macros. It verifies true assertions pass, false assertions abort or throw depending on abort-disabling mode, and assertion messages include source context and backtraces.

Important APIs and types: Uses `cpp-utils/assert/assert.h`, GoogleTest death/exception assertions, and GoogleMock matchers for message checks.

Control flow: Tests trigger `ASSERT` with true and false expressions, switch the assertion system into non-aborting mode for throw checks, and inspect generated diagnostic strings.

State and persistence behavior: State is process-local assertion configuration and captured death-test subprocess output. No files are persisted.

Dependencies and integration points: Couples assertion macros to backtrace formatting and platform-specific death-test behavior.

Risks: Death tests can be platform/compiler sensitive. Backtrace string content changes may break regex expectations even if failure reporting remains useful.

Test signals: No death for true conditions, death or exception for false conditions, expected message text, and backtrace presence.
