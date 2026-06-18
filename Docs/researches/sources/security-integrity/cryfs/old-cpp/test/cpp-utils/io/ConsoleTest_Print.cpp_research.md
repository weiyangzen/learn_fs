# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_Print.cpp

Purpose: Tests simple console printing through the shared console fixture.

Important APIs and types: Uses `ConsoleTest::print` and output-line assertion helpers.

Control flow: The test prints content through the `IOStreamConsole` wrapper and asserts the expected output line appears.

State and persistence behavior: Output is captured through in-memory pipe streams. No files or terminal state are persisted.

Dependencies and integration points: Validates the basic output path used by CLI prompts and status messages.

Risks: Narrow coverage; formatting changes outside basic print behavior are covered by specific prompt tests.

Test signals: Captured stdout line equals expected print text.
